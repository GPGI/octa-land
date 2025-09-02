// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "lib/openzeppelin-contracts/contracts/token/ERC1155/ERC1155.sol";
import "lib/openzeppelin-contracts/contracts/access/Ownable.sol";

contract LandRegistry is ERC1155, Ownable {
    uint256 public nextPlotId = 1;
    mapping(uint256 => address) public plotOwners;

    // Pass initialOwner to Ownable
    constructor(address initialOwner) 
        ERC1155("https://octa.city/api/lands/{id}.json") 
        Ownable(initialOwner) 
    {}

    function mintLand(address to) external onlyOwner {
        uint256 plotId = nextPlotId;
        nextPlotId++;
        _mint(to, plotId, 1, "");
        plotOwners[plotId] = to;
    }

    function transferLand(address from, address to, uint256 plotId) external {
        require(plotOwners[plotId] == from, "Not land owner");
        safeTransferFrom(from, to, plotId, 1, "");
        plotOwners[plotId] = to;
    }
}
