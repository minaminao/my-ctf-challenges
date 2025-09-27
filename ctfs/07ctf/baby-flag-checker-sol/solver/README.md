# Brief Writeup

A small anti-decompilation trick has been applied: PUSH2 0x000f (61000f) -> PUSH1 0x00 SLOAD (600054).
So no proper decompilation result can be obtained.

From the disassembly and dynamic analysis, it's clear that the contract is only performing simple addition and multiplication, so it can be easily solved using a symbolic execution engine such as [hevm](https://github.com/argotorg/hevm).

**Flag**: `07CTF{MVdfJ892Xb}`
