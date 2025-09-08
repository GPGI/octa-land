// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./Interfaces.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @title Treasury
/// @notice Holds Octavia & Sarakt balances in xBGL. Owner (admin multisig) can withdraw.
contract Treasury is Ownable {
    IERC20Minimal public xBGL;

    uint256 public octaviaBalance;
    uint256 public saraktBalance;

    event DepositedOctavia(address indexed from, uint256 amount);
    event DepositedSarakt(address indexed from, uint256 amount);
    event WithdrawnOctavia(address indexed to, uint256 amount);
    event WithdrawnSarakt(address indexed to, uint256 amount);

    constructor(address _xBGL) {
        require(_xBGL != address(0), "xBGL zero");
        xBGL = IERC20Minimal(_xBGL);
    }

    /// deposit tokens to Octavia balance (caller must approve to this contract)
    function depositOctavia(uint256 amount) external {
        require(amount > 0, "zero");
        require(xBGL.transferFrom(msg.sender, address(this), amount), "transferFrom failed");
        octaviaBalance += amount;
        emit DepositedOctavia(msg.sender, amount);
    }

    /// deposit tokens to Sarakt balance (caller must approve)
    function depositSarakt(uint256 amount) external {
        require(amount > 0, "zero");
        require(xBGL.transferFrom(msg.sender, address(this), amount), "transferFrom failed");
        saraktBalance += amount;
        emit DepositedSarakt(msg.sender, amount);
    }

    /// withdraw octavia funds (onlyOwner multisig/admin)
    function withdrawOctavia(address to, uint256 amount) external onlyOwner {
        require(to != address(0), "zero");
        require(octaviaBalance >= amount, "insufficient");
        octaviaBalance -= amount;
        require(xBGL.transfer(to, amount), "transfer failed");
        emit WithdrawnOctavia(to, amount);
    }

    /// withdraw sarakt funds (onlyOwner)
    function withdrawSarakt(address to, uint256 amount) external onlyOwner {
        require(to != address(0), "zero");
        require(saraktBalance >= amount, "insufficient");
        saraktBalance -= amount;
        require(xBGL.transfer(to, amount), "transfer failed");
        emit WithdrawnSarakt(to, amount);
    }

    function balances() external view returns (uint256 oct, uint256 sar) {
        return (octaviaBalance, saraktBalance);
    }
}
