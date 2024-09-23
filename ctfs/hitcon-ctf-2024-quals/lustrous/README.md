# Lustrous

**Lustrous** is a Vyper challenge created for HITCON CTF 2024 Quals.

This directory includes:
- `server`: the challenge server based on https://github.com/minaminao/tokyo-payload
- `solver`: the author's solver

The challenge contract is [land_of_the_lustrous.vy](server/src/contracts/land_of_the_lustrous.vy).

NOTE: This version has been revised to address an unintended solution.

## Description

"In a world inhabited by crystalline lifeforms called The Lustrous, every unique gem must fight for their way of life against the threat of lunarians who would turn them into decorations." – Land of the Lustrous

```
nc lustrous.chal.hitconctf.com 31337
```

## Generate the distributed files

```
make generate-distfiles
```

## Launch a challenge server

```
make start-challenge-server
```

## Access the challenge server

```
nc localhost 31337
```

Good luck!

---

## Writeup

[Brief Writeup](solver/README.md)

## Run the author's solver

Local:
```
make run-solver
```

Remote:
```
make run-solver-remote
```
