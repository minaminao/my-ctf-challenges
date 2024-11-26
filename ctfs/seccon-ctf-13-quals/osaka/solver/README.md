# SECCON CTF 13 Quals - OSAKA - Author Writeup

The goal of this challenge is to make the `isSolved` function in the `OSAKA` contract, implemented using [EVM Object Format (EOF)](https://evmobjectformat.org/), return `true`.
The EOF contract was created using [forge-eof](https://github.com/paradigmxyz/forge-eof) released by Paradigm, which internally utilizes the [Solidity PoC](https://github.com/ipsilon/solidity) developed by the Ipsilon team.
The infrastructure is configured to enable EOF by using the `--odyssey` option in Anvil ([ref](https://www.ithaca.xyz/updates/odyssey)).

To make `isSolved()` return `true`, the `challenge` function must be fully executed, which includes running `sstore(isSolved.slot, true)`.
Thus, you must win two games: `StickGame` and `ChronoGame`.

However, it looks impossible to win either game under normal situations.
- For `StickGame`, a variation of [Nim](https://en.wikipedia.org/wiki/Nim), the computer is programmed always to win.
- For `ChronoGame`, winning requires waiting around 100 years.

So, what should you do?

Actually, there are two vulnerabilities related to EOF in this contract.
Exploiting them will help you solve this challenge.

## Vuln 1: Contract Recreation Failures

EOF introduces the `EOFCREATE` instruction for contract creation, deprecating the traditional `CREATE` and `CREATE2`.
When using `EOFCREATE`, a `salt` must be specified, similar to the behavior of the old `CREATE2`.

As a result, Solidity cannot redeploy the same bytecode contract without specifying a `salt`.
For example, the following code, which worked previously, will no longer execute (at least with the currently available Solidity PoC):

```solidity
new Contract(); // success
new Contract(); // fail 🤯
```

In this challenge, the `initializeGame` function is called from the `challenge` function to generate a `StickGame`.
However, if you directly call `initializeGame` beforehand and deploy a `StickGame`, the contract creation in the `challenge` function will fail.
By doing so, you can freely set the `initialSticks` for the `StickGame` and win the first game.

## Vuln 2: Call Return Mishandling

EOF uses the `EXTCALL` instruction for contract calls, deprecating the traditional `CALL` instruction, as well as `DELEGATECALL` and `STATICCALL`.

Unlike `CALL`, `EXTCALL` can return **three** values:
- `0`: success
- `1`: revert
- `2`: failure

In this contract, the return value of the `EXTCALL` instruction is checked while playing the game.

However, there is a vulnerability that a `2` (failure) return value is treated as a win:

```solidity
let reverted := extcall(gameMasterAddr, 0x1c, 0x44, 0)
if eq(reverted, true) { win := false }
```

Then, how can you achieve a return value of `2`?

In this challenge, you can trigger an Out-of-Gas condition to make `EXTCALL` return `2`.
This means that during `playGame` for the second game, `ChronoGame`, you need to trigger an Out-of-Gas condition.
The required gas limit can be calculated in some way (e.g., manual/programmatic binary search).

With this, you will win the second game.

## Final Step: Access Set

The above vulnerabilities will allow you to reach the final `sstore(isSolved.slot, true)`.

However, since the Out-of-Gas condition was triggered during the `playGame` call, the remaining gas will be insufficient to execute `SSTORE`, causing the transaction to revert due to Out-of-Gas.

This issue can be resolved by using an access set ([ref](https://www.evm.codes/about#access_list)).
Specifically, by calling the `isSolved` function before invoking `challenge` within the same transaction, you can save gas and write the `isSolved` slot.

## Exploit

The final exploit looks like this:

```solidity
contract Exploit {
    function exploit(OSAKA osaka) public {
        osaka.isSolved(); // for access set
        osaka.gameMaster().initializeGame(1, 1);
        osaka.challenge();
    }

    function solve(uint256 sticks) public pure returns (uint256) {
        return sticks;
    }
}
```

Deploy this contract and call the `exploit` function with a proper gas limit (e.g., `4632905`):

```
cast send $EXPLOIT_ADDR "exploit(address)" $INSTANCE_ADDR --private-key $PRIVATE_KEY --gas-limit 4632905
```

**Flag:** `SECCON{d3vc0n_054k4_w4s_fun_a8b3bdaa46f7d7d5}`

The exploit looks simple, but the challenge itself introduced some novel ideas, making it difficult to come up with a solution.
In fact, only two teams managed to solve it. Congratulations!
