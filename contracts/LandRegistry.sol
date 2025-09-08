// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./Interfaces.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @title LandRegistry (Phase1)
/// @notice Simple plot registry. Plots are not ERC721 here (Phase1 simple registry).
///         Integrates with Treasury and Mortgage contracts via addresses.
contract LandRegistry is Ownable {
    IERC20Minimal public xBGL;
    address public treasuryAddress;   // Treasury contract address (where fees are forwarded)
    address public mortgageManager;   // Mortgage contract authorized to place liens

    uint256 public totalPlots;
    uint256 public plotsMinted;

    // Economics (values denominated in xBGL smallest unit - admin sets to match decimals)
    uint256 public plotPrice;          // e.g., 400 * 1e18
    uint256 public docFee;             // 150 * 1e18
    uint256 public editFee;            // 5 * 1e18
    uint256 public ownershipChangeFee; // admin set (xBGL equivalent of 30 EUR)
    uint256 public commissionNumerator;    // 89 => 8.9%
    uint256 public commissionDenominator;  // 1000
    uint256 public treasuryShareNumerator; // 70
    uint256 public treasuryShareDenominator; // 100

    struct Plot {
        uint256 id;
        uint256 areaM2;
        address owner;
        uint256 netValue;   // last market price (xBGL)
        bool activated;
        bool forSale;
        uint256 salePrice;  // listing price in xBGL
        bool lien;
    }

    mapping(uint256 => Plot) public plots;

    event PlotMinted(uint256 indexed plotId, uint256 areaM2, address indexed to);
    event PrimarySold(uint256 indexed plotId, address indexed buyer, uint256 paid);
    event SecondaryListed(uint256 indexed plotId, uint256 price);
    event SecondarySold(uint256 indexed plotId, address indexed buyer, uint256 price);
    event LienPlaced(uint256 indexed plotId);
    event LienReleased(uint256 indexed plotId);

    modifier onlyMortgageManager() {
        require(msg.sender == mortgageManager, "not mortgage manager");
        _;
    }

    constructor(
        address _xBGL,
        address _treasury,
        uint256 _totalPlots,
        uint256 _plotPrice,
        uint256 _docFee,
        uint256 _editFee
    ) {
        require(_xBGL != address(0), "xBGL zero");
        xBGL = IERC20Minimal(_xBGL);
        treasuryAddress = _treasury;
        totalPlots = _totalPlots;
        plotPrice = _plotPrice;
        docFee = _docFee;
        editFee = _editFee;
        ownershipChangeFee = 0;
        commissionNumerator = 89;
        commissionDenominator = 1000;
        treasuryShareNumerator = 70;
        treasuryShareDenominator = 100;
    }

    // --- admin functions ---
    function setTreasuryAddress(address _treasury) external onlyOwner {
        treasuryAddress = _treasury;
    }

    function setMortgageManager(address _mgr) external onlyOwner {
        mortgageManager = _mgr;
    }

    function setOwnershipChangeFee(uint256 amount) external onlyOwner {
        ownershipChangeFee = amount;
    }

    function setPlotPrice(uint256 price) external onlyOwner {
        plotPrice = price;
    }

    function setDocFee(uint256 fee) external onlyOwner {
        docFee = fee;
    }

    // mint plots in batches, assign to `to` (admin typically)
    function mintPlots(uint256 startId, uint256 count, uint256 areaM2, address to) external onlyOwner {
        require(count > 0, "count0");
        require(plotsMinted + count <= totalPlots, "exceed total");
        for (uint256 i = 0; i < count; i++) {
            uint256 id = startId + i;
            require(plots[id].id == 0, "already minted");
            plots[id] = Plot({
                id: id,
                areaM2: areaM2,
                owner: to,
                netValue: 0,
                activated: true,
                forSale: false,
                salePrice: 0,
                lien: false
            });
            plotsMinted++;
            emit PlotMinted(id, areaM2, to);
        }
    }

    function activatePlot(uint256 plotId) external onlyOwner {
        require(plots[plotId].id != 0, "no plot");
        plots[plotId].activated = true;
    }

    // --- primary purchase (buyer buys 'from owner' paying plotPrice) ---
    function buyPrimary(uint256 plotId) external {
        Plot storage p = plots[plotId];
        require(p.activated, "not active");
        require(p.owner != msg.sender, "already owner");

        uint256 totalPrice = plotPrice;
        require(xBGL.transferFrom(msg.sender, address(this), totalPrice), "payment failed");

        // compute shares
        uint256 saraktAmount = (totalPrice * treasuryShareNumerator) / treasuryShareDenominator; // 70%
        uint256 commissionAmount = (totalPrice * commissionNumerator) / commissionDenominator; // 8.9%
        uint256 octaviaAmount = commissionAmount + docFee;

        // forward treasury amounts if treasury assigned, else keep in contract
        if (treasuryAddress != address(0)) {
            // transfer sarakt + octavia to treasuryAddress
            require(xBGL.transfer(treasuryAddress, saraktAmount + octaviaAmount), "transfer to treasury failed");
        }

        // pay remaining to seller (owner)
        uint256 net = totalPrice - saraktAmount - octaviaAmount;
        if (p.owner != address(0)) {
            require(xBGL.transfer(p.owner, net), "pay owner failed");
        }

        // set new owner and netValue
        p.owner = msg.sender;
        p.netValue = totalPrice;

        emit PrimarySold(plotId, msg.sender, totalPrice);
    }

    // --- secondary listing ---
    function listPlotForSale(uint256 plotId, uint256 priceXbgl) external {
        Plot storage p = plots[plotId];
        require(p.owner == msg.sender, "not owner");
        require(!p.lien, "lien");
        p.forSale = true;
        p.salePrice = priceXbgl;
        emit SecondaryListed(plotId, priceXbgl);
    }

    // buyer pays salePrice + buyer commission. seller receives salePrice - seller commission.
    // Both commissions + ownershipChangeFee + editFee forwarded to treasuryAddress if set.
    function buySecondary(uint256 plotId) external {
        Plot storage p = plots[plotId];
        require(p.forSale, "not for sale");
        require(p.owner != msg.sender, "already owner");
        require(!p.lien, "lien on plot");

        uint256 salePrice = p.salePrice;
        uint256 commissionAmount = (salePrice * commissionNumerator) / commissionDenominator;
        uint256 buyerCommission = commissionAmount;
        uint256 sellerCommission = commissionAmount;
        uint256 totalRequired = salePrice + buyerCommission; // buyer must pay sale + buyer commission

        require(xBGL.transferFrom(msg.sender, address(this), totalRequired), "payment failed");

        // pay seller: salePrice - sellerCommission
        uint256 sellerReceive = salePrice - sellerCommission;
        require(xBGL.transfer(p.owner, sellerReceive), "pay seller failed");

        // forward commissions + ownershipChangeFee + editFee to treasury
        uint256 totalCommsAndFees = buyerCommission + sellerCommission + ownershipChangeFee + editFee;
        if (treasuryAddress != address(0)) {
            require(xBGL.transfer(treasuryAddress, totalCommsAndFees), "transfer to treasury failed");
        }

        // change ownership and net value
        p.owner = msg.sender;
        p.netValue = salePrice;
        p.forSale = false;
        p.salePrice = 0;

        emit SecondarySold(plotId, msg.sender, salePrice);
    }

    // liens handled by Mortgage manager
    function placeLien(uint256 plotId) external onlyMortgageManager {
        Plot storage p = plots[plotId];
        require(!p.lien, "already liened");
        p.lien = true;
        emit LienPlaced(plotId);
    }

    function releaseLien(uint256 plotId) external onlyMortgageManager {
        Plot storage p = plots[plotId];
        require(p.lien, "no lien");
        p.lien = false;
        emit LienReleased(plotId);
    }

    // admin getters
    function getPlot(uint256 id) external view returns (
        uint256 plotId, uint256 areaM2, address owner, uint256 netValue, bool activated, bool forSale, uint256 salePrice, bool lien
    ) {
        Plot storage p = plots[id];
        return (p.id, p.areaM2, p.owner, p.netValue, p.activated, p.forSale, p.salePrice, p.lien);
    }
}
