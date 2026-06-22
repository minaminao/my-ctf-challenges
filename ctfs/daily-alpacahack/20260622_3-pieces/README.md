# Author's Writeup for ✌️✌️✌️

Daily AlpacaHack で 6/22 に出題した『✌️✌️✌️』の作問者 Writeup です。

https://alpacahack.com/daily/challenges/3-pieces

## 問題概要

問題文:
```
人にやさしく
```

問題スクリプト:
```python
import os, secrets

P = 2**521 - 1
THRESHOLD = 3
SHARES = 4

flag = int.from_bytes(os.getenv("FLAG", "Alpaca{DUMMY}").encode())
assert flag < P

coeffs = [flag] + [secrets.randbelow(P - 1) + 1 for _ in range(THRESHOLD - 1)]

# f(x) = c0 + c1 * x + c2 * x^2 mod P
f = lambda x: sum(c * pow(x, i, P) for i, c in enumerate(coeffs)) % P

# shares = (1, f(1)), ..., (4, f(4))
shares = [(x, f(x)) for x in range(1, SHARES + 1)]

# 3-out-of-4 secret sharing
print(f"{shares[:THRESHOLD] = }")
```

秘密分散がテーマの問題です。

## 解法

未知数が `c0`, `c1`, `c2` の 3 個あり、その一次方程式が 3 つ与えられます:
- c0 + c1 + c2 = y0
- c0 + 2 c1 + 4 c2 = y1
- c0 + 3 c1 + 9 c2 = y2

これを素直に解けばOKです。

`c0` を消して:
- c1 + 3 c2 = y1 - y0
- 2 c1 + 8 c2 = y2 - y0

`c1` を消すと:
- c2 = (y2 - y0 - 2 (y1 - y0)) (2^-1)

よって:
- c1 = y1 - y0 - 3 c2
- c0 = y0 - c1 - c2

これで `flag` である `c0` が求まり、解けました。

Solver:

```python
import ast
from Crypto.Util.number import long_to_bytes

P = 2**521 - 1
THRESHOLD = 3

with open("../distfiles/output.txt") as f:
    shares = ast.literal_eval(f.readline().split(" = ")[1])

y0, y1, y2 = [y for _, y in shares]

c2 = (y2 - y0 - 2 * (y1 - y0)) * pow(2, -1, P) % P
c1 = (y1 - y0 - 3 * c2) % P
c0 = (y0 - c1 - c2) % P

print(long_to_bytes(c0))
```

Flag: `Alpaca{try_lagrange_interpolation_too}`

ラグランジュ補間でも解けます。
