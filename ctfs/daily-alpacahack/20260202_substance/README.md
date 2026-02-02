# Author's Writeup for Substance

Daily AlpacaHack で 2/2 に出題した『Substance』の作問者 Writeup です。

https://alpacahack.com/daily/challenges/substance

## 問題概要

問題文:
```
😇 😈
```

添付ファイルには次の Python スクリプト `chal.py` とその出力 `output.txt` が含まれています。
```python
import os
from random import randint

flag = int.from_bytes(os.getenv("FLAG", "Alpaca{REDACTED}").encode(), "big")
print(flag * randint(2, 2026) * randint(2, 2026) * randint(2, 2026))
print(flag * randint(2, 2026) * randint(2, 2026) * randint(2, 2026))
```

フラグが文字列から整数に変換され、それに3つの乱数（2~2026）を掛けた値が2つ出力されています。

## 解法

出力の1つ目の値と2つ目の値をそれぞれ `x`, `y` とします。

まず `gcd(x,y)` を計算すると、 
```
flag * gcd(xの乱数部分,yの乱数部分)
```
が得られます。

ここで `gcd(xの乱数部分,yの乱数部分)` がわかれば、`flag` が求まります。

では `gcd(xの乱数部分,yの乱数部分)` はどれくらいの値になるでしょうか。

直感的に、独立な乱数同士の最大公約数は小さくなることが期待できます。そのため、ちょっと試し割りすれば `flag` が求まりそうです。

実際、2つの乱数について考えると、
- ある乱数が2の倍数になる確率は 1/2 なので、最大公約数が 2 の倍数になるのは 1/2 × 1/2 の 1/4
- ある乱数が3の倍数になる確率は 1/3 なので、最大公約数が 3 の倍数になるのは 1/3 × 1/3 の 1/9
- ある乱数が5の倍数になる確率は 1/5 なので、最大公約数が 5 の倍数になるのは 1/5 × 1/5 の 1/25

このように、乱数同士の最大公約数がnの倍数になる確率は、nが大きくなるにつれ指数的に小さくなります。

今回は、3つの乱数を掛けた値ですが、その最大公約数も同様、大きな数の倍数になる確率は非常に小さくなります。
- 3の倍数になる確率は $(1 - \frac{2}{3}^3)^2$ で約 0.5
- 11の倍数になる確率は $(1 - \frac{10}{11}^3)^2$ で約 0.06
- 101の倍数になる確率は $(1 - \frac{100}{101}^3)^2$ で約 0.0008

ということで、大きく見積もっても 10000 くらいまで試し割りすればフラグが求まりそうです（作問者がかなり意図的に出力を選んでいなければ）。

よって、以下のソルバーでフラグを復元できます。

```python
import math
from Crypto.Util.number import long_to_bytes

x = 70430356624056699219964353455091734195306937238245707901514922333654568000660
y = 5585179348150525015655680494025565656820428601640301759505137819334580532521858
g = math.gcd(x, y)

for i in range(1, 10000):
    if g % i == 0:
        flag = long_to_bytes(g // i)
        if flag.startswith(b"Alpaca"):
            print(i, flag)
```

実行結果:
```
$ python solve.py
18 b'Alpaca{will_ch4nge_y0ur_lif3}'
```

Flag: `Alpaca{will_ch4nge_y0ur_lif3}`
