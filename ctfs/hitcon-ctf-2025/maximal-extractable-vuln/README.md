# Maximal Extractable Vuln

**Maximal Extractable Vuln** is a blockchain challenge created for HITCON CTF 2025.

This directory includes:
- [distfiles](./distfiles/): the distributed files for players
- [server](./server/): the challenge server based on [my previous challenge](https://github.com/minaminao/my-ctf-challenges/tree/main/ctfs/seccon-ctf-13-quals/trillion-ether).
- [solver](./solver/): the author's solver and writeup.

## Description

A newly deployed, simple Uniswap V4 arbitrage contract has been identified 🤖

```
nc maximal-extractive-vuln.chal.hitconctf.com 31337
```

## Launch a challenge server

Set the `FORKING_RPC_URL` in `compose.yaml` to your mainnet RPC endpoint (for example, Alchemy) to deploy the challenge contract on a network forked from the Ethereum mainnet.

Run:
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
