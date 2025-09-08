// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// Minimal IERC20 interface used by Phase1 contracts.
/// Assumes xBGL token already exists and follows ERC20 standard.
interface IERC20Minimal {
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address owner) external view returns (uint256);
}
