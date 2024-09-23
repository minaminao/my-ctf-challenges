# Solver

## Brief Writeup

A Vyper contract is provided.
After thoroughly reading it, only a minor reentrancy vulnerability is found, making it unsolvable.
This leads to suspicions of a bug in the compiler's bytecode generation.

On investigating for exploitable vulnerabilities, it is discovered that the `concat` built-in function has a vulnerability (ref: [CVE-2024-22419](https://github.com/vyperlang/vyper/security/advisories/GHSA-2q8v-3gqq-4f8p)).
This vulnerability means that when a function F calls `concat`, the leading bytes of the first variable declared in the function G that calls F is overwritten with zero.
By combining this with the reentrancy vulnerability, it is possible to overwrite the leading bytes of the negative health value with zero, making the value very large.
This gives a significant advantage in battles.

Further investigating reveals that the return value of a call undergoes internal ABI decoding.
This leads to the realization that an ABI decoding vulnerability can be exploited (ref: [CVE-2024-26149](https://github.com/vyperlang/vyper/security/advisories/GHSA-9p8r-4xp4-gw5w)).
Specifically, by setting the read position of the dynamic array in the return value to a negative value, it is possible to copy the lunarian's actions, resulting in a complete draw.
If all rounds end in a draw, the side with the higher health wins, providing a way to clear the final stage.

Finally, by strategically combining these vulnerabilities and progressing/retreating through the stages, this challenge is solved.
The lunarian's unpredictable behavior can be managed through conditional branching based on state and return values, along with strategic use of `revert`.
