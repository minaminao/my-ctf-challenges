// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

struct Gem {
    int256 health;
    int256 max_health;
    int256 attack;
    int256 hardness;
    uint256 status;
}

interface ILandOfTheLustrous {
    function roles(address) external returns (uint256);
    function sequences(address) external returns (uint32);
    function stage() external returns (uint8);
    function gems(bytes32) external returns (Gem memory);
    function assigned_gems(address) external returns (uint32);
    function continued(address) external returns (bool);

    function register_master() external;
    function create_gem() external payable returns (Gem memory);
    function merge_gems() external returns (Gem memory);
    function pray_gem() external;
    function assign_gem(uint32 sequence) external;
    function battle(uint8[] memory lunarian_actions) external returns (bool, int256, int256);
    function continue_battle() external payable;
    function is_solved() external returns (bool);
}
