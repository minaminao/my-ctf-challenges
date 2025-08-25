# Solver

## Brief Writeup

You are given the `Setup` contract and the bytecode of a simple Uniswap V4 arbitrage contract in it.
The goal is to drain funds from the arbitrage contract.

The entry point of the arbitrage is the `execute` function.
When this is called, the `POOL_MANAGER` becomes unlocked, and then `unlockCallback` is invoked.
Eventually, any profit is transferred to `ORIGIN`.
If no profit is made, the execution fails.

The first vulnerability lies in `unlockCallback`. The access is not restricted to `POOL_MANAGER`, so anyone can call it.

The second vulnerability is that the arbitrage contract fails to consider EIP-7702.
This challenge network is a fork of mainnet, and this allows you to set code on `ORIGIN`, which enables a reentrancy attack through `ORIGIN`.

Thus, you first need to generate profit so that funds are sent to `ORIGIN`.
There are multiple ways to achieve this.
One straightforward idea is to construct an arbitrage path using your own custom token.

After that, `unlockCallback` can be called to drain funds from the `POOL_MANAGER`.
However, since the `POOL_MANAGER` is not unlocked at that point, direct transfers will throw an error.
To bypass this, you first wrap the call in `unlock`, and then execute it.
The resulting call stack looks like this: `ORIGIN` -> `unlockCallback` -> `unlock` -> `unlockCallback` -> transfer logic.

The concrete exploit is implemented in:
* [Exploit.s.sol](./src/Exploit.s.sol)
* [Exploit.sol](./src/Exploit.sol)
