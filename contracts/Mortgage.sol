// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./Interfaces.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

interface ILandRegistry {
    function plots(uint256) external view returns (
        uint256 id, uint256 areaM2, address owner, uint256 netValue, bool activated, bool forSale, uint256 salePrice, bool lien
    );
    function placeLien(uint256 plotId) external;
    function releaseLien(uint256 plotId) external;
}

contract Mortgage is Ownable {
    IERC20Minimal public xBGL;
    ILandRegistry public landRegistry;
    address public treasuryAddress;

    uint256 public minDownNum = 10;  // 10%
    uint256 public minDownDen = 100;
    uint256 public interestNum = 10; // 10% simplified (annualized in expanded versions)
    uint256 public interestDen = 100;

    uint256 public loanCounter;

    struct Loan {
        uint256 id;
        uint256 plotId;
        address borrower;
        address seller;
        uint256 principal; // remaining principal
        uint256 originalPrincipal;
        uint256 createdAt;
        bool active;
    }

    mapping(uint256 => Loan) public loans;

    event MortgageCreated(uint256 indexed loanId, uint256 plotId, address borrower, uint256 principal);
    event MortgagePayment(uint256 indexed loanId, uint256 amount, uint256 remaining);
    event MortgageClosed(uint256 indexed loanId);

    constructor(address _xBGL, address _landRegistry, address _treasury) {
        require(_xBGL != address(0), "xBGL0");
        xBGL = IERC20Minimal(_xBGL);
        landRegistry = ILandRegistry(_landRegistry);
        treasuryAddress = _treasury;
    }

    function createMortgage(uint256 plotId, uint256 offeredSalePrice) external {
        // read plot details
        ( , , address seller, uint256 netValue, bool activated, , , bool lien) = landRegistry.plots(plotId);
        require(activated, "not active");
        require(!lien, "already liened");
        require(seller != address(0), "no seller");
        require(seller != msg.sender, "already owner");

        uint256 salePrice = offeredSalePrice;
        uint256 minDown = (salePrice * minDownNum) / minDownDen;

        // transfer down payment from buyer
        require(xBGL.transferFrom(msg.sender, address(this), minDown), "downpayment failed");

        // place lien on plot
        landRegistry.placeLien(plotId);

        uint256 principal = salePrice - minDown;
        loanCounter++;
        loans[loanCounter] = Loan({
            id: loanCounter,
            plotId: plotId,
            borrower: msg.sender,
            seller: seller,
            principal: principal,
            originalPrincipal: principal,
            createdAt: block.timestamp,
            active: true
        });

        // transfer down payment to seller (seller receives down immediately)
        require(xBGL.transfer(seller, minDown), "transfer to seller failed");

        emit MortgageCreated(loanCounter, plotId, msg.sender, principal);
    }

    /// @notice borrower pays amount in xBGL. For simplicity, payments are forwarded to treasuryAddress.
    function payMortgage(uint256 loanId, uint256 amount) external {
        Loan storage L = loans[loanId];
        require(L.active, "not active");
        require(L.borrower == msg.sender, "not borrower");
        require(amount > 0, "zero");

        require(xBGL.transferFrom(msg.sender, address(this), amount), "transfer failed");

        // forward to treasury
        if (treasuryAddress != address(0)) {
            require(xBGL.transfer(treasuryAddress, amount), "forward failed");
        }

        if (amount >= L.principal) {
            uint256 refund = amount - L.principal;
            L.principal = 0;
            L.active = false;
            // release lien
            landRegistry.releaseLien(L.plotId);
            if (refund > 0) {
                require(xBGL.transfer(msg.sender, refund), "refund failed");
            }
            emit MortgagePayment(loanId, amount, 0);
            emit MortgageClosed(loanId);
        } else {
            L.principal -= amount;
            emit MortgagePayment(loanId, amount, L.principal);
        }
    }

    // admin function to handle defaults (seize / transfer) - simplified
    function adminCloseAndSeize(uint256 loanId) external onlyOwner {
        Loan storage L = loans[loanId];
        require(L.active, "not active");
        L.active = false;
        landRegistry.releaseLien(L.plotId);
        emit MortgageClosed(loanId);
    }
}
