# Trillion Ether

**Trillion Ether** is a warmup blockchain challenge created for SECCON CTF 13 Quals.

This directory includes:
- `build`: the challenge server based on [my previous challenge](../../hitcon-ctf-2024-quals/lustrous/).
- `solver`: the author's solver

Solves: 35 / 653 teams in 24h.

## Description

Get Chance!

```
nc trillion-ether.seccon.games 31337
```

## Contract

The challenge contract is [TrillionEther.sol](build/src/contracts/src/TrillionEther.sol):

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.28;

contract TrillionEther {
    struct Wallet {
        bytes32 name;
        uint256 balance;
        address owner;
    }

    Wallet[] public wallets;

    constructor() payable {
        require(msg.value == 1_000_000_000_000 ether);
    }

    function isSolved() external view returns (bool) {
        return address(this).balance == 0;
    }

    function createWallet(bytes32 name) external payable {
        wallets.push(_newWallet(name, msg.value, msg.sender));
    }

    function transfer(uint256 fromWalletId, uint256 toWalletId, uint256 amount) external {
        require(wallets[fromWalletId].owner == msg.sender, "not owner");
        wallets[fromWalletId].balance -= amount;
        wallets[toWalletId].balance += amount;
    }

    function withdraw(uint256 walletId, uint256 amount) external {
        require(wallets[walletId].owner == msg.sender, "not owner");
        wallets[walletId].balance -= amount;
        payable(wallets[walletId].owner).transfer(amount);
    }

    function _newWallet(bytes32 name, uint256 balance, address owner) internal returns (Wallet storage wallet) {
        wallet = wallet;
        wallet.name = name;
        wallet.balance = balance;
        wallet.owner = owner;
    }
}
```

## Writeup

-> [solver/README.md](solver/README.md)

## Launch a challenge server

```
make start-challenge-server-local
```

## Access the challenge server

```
nc localhost 31337
```

Good luck!

## Run the author's solver

```
make run-solver-local
```
