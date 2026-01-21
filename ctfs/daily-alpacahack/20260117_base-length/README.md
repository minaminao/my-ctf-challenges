# Author's Writeup for Base Length

Daily AlpacaHack で 1/17 に出題した『Base Length』の作問者 Writeup です。

https://alpacahack.com/daily/challenges/base-length

## 問題概要

問題文:
```
Base32 より Base64 のほうが効率的って聞きました！
```

添付ファイルには次の Python スクリプトが含まれています:
```python
from base64 import b32decode, b64decode

b32 = input("Base32: ")
b64 = input("Base64: ")

assert b32.count("=") == 0 and b64.count("=") == 0, "Don't use padding!"
assert b32decode(b32) == b64decode(b64), "Decoded values are not equal!"

# Base32: 5 bits -> 1 char,
# Base64: 6 bits -> 1 char, so ...
if len(b32) >= len(b64):
    print("Expected :)")
else:
    # never reach here :)
    print("Wow... The flag is Alpaca{**** REDACTED ****}")
```

Base64 エンコーディングは、CTF でも実世界でもよく使われている有名な方式ですが、Base32 という亜種も存在します。
この問題は Base32 と Base64 の性質をテーマとした問題です。

前提として、まず、Base64 はデータを 64 種の文字で表します:
```
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
```

具体的には、データを 6 ビットずつに分割し、それを 1 文字に対応させます。
$2^6 = 64$ であることから、Base64 というわけです。

一方で、 Base32 はデータを 32 種の文字で表します:
```
ABCDEFGHIJKLMNOPQRSTUVWXYZ234567
```

Base32 では、データを 5 ビットずつに分割して割り当てます。

与えられたスクリプトを読むと、Base32 エンコードされた文字列と Base64 エンコードされた文字列を入力として受け取ります。
ただし、以下の条件を満たす必要があります:
- パディングを含めてはいけない
- デコード結果が同一である

このとき、`(Base32 エンコードされた文字列長) >= (Base64 エンコードされた文字列長)` の条件を満たさなければ、フラグが出力されます。

Base32 は 5 ビットを 1 バイト (= 8 ビット)、 Base64 は 6 ビットを 1 バイト (= 8 ビット) に変換するので、どちらのエンコーディングもエンコードを行うことでデータ量が増加します。
しかし、分割するビット数の違いから、 Base64 のほうが Base32 よりデータ量の増大が抑えられるので効率的です。

つまり、同じ文字列をそれぞれでエンコードした場合、 Base32 のほうが文字列長が長くなるため、この条件を破ることは不可能に見えます。

## 解法

理論上は解けないので、実装上の挙動を疑います。

そこで、 `b32decode` と `b64decode` の仕様を見てみます: https://docs.python.org/ja/3.14/library/base64.html 。

`b32decode` の説明には、特に使えそうな挙動はありません。

一方で、 `b64decode` の説明には以下の興味深い記述があります:

> `validate` が `False` (デフォルト) の場合、標準の base64 アルファベットでも代替文字でもない文字はパディングチェックの前に無視されます。
> `validate` が `True` の場合、入力に base64 アルファベット以外の文字があると `binascii.Error` を発生させます。

つまり、 `b64decode` では、入力に Base64 の規定の文字以外の文字をデフォルトで含められるようです。
これは、`b32decode` の挙動とは異なります:

> `s` が正しくパディングされていない場合や、入力にアルファベットでない文字が含まれていた場合に、 `binascii.Error` 例外を発生させます。

この `b64decode` の挙動を利用します。
実際に `b64deocde` に規定の文字以外を含められるか確認してみます:

```
>>> from base64 import *
>>> b64encode(b"HELLO")
b'SEVMTE8='
>>> b64decode(b"SEVMTE8=")
b'HELLO'
>>> b64decode(b"!!S!!E!!V!!M!!T!!E!!8!!=!!")
b'HELLO'
```

`!` を含めても正しく `HELLO` にデコードされました。
後はこの挙動を利用した入力を作るだけです。

パディングは含められないので、エンコード結果にパディングが含まれない条件を考えます:
- Base32 では 5 ビットごとに分割するので、 `(エンコードされる文字列長) * 8` が 5 で割り切れればパディング無し
- Base64 では 6 ビットごとに分割するので、 `(エンコードされる文字列長) * 8` が 6 で割り切れればパディング無し

よって、長さ 5 * 3 = 15 の適当な文字列が使えます:
```
>>> b32encode(b"A"*15)
b'IFAUCQKBIFAUCQKBIFAUCQKB'
>>> b64encode(b"A"*15)
b'QUFBQUFBQUFBQUFBQUFB'
```

あとは Base64 でエンコードされた文字列のほうが長くなるように `!!!!!` を付加して、その文字列を送ればフラグが得られます:

```
$ nc 34.170.146.252 60350
Base32: IFAUCQKBIFAUCQKBIFAUCQKB
Base64: QUFBQUFBQUFBQUFBQUFB!!!!!
Wow... The flag is Alpaca{BASE32ISSUPERIOR}
```

ちなみに、空文字列もデコード可能であり 0 は 15 の倍数なので、空文字列を使って解くこともできます:

```
$ nc 34.170.146.252 60350
Base32: 
Base64: !
Wow... The flag is Alpaca{BASE32ISSUPERIOR}
```

Flag: `Alpaca{BASE32ISSUPERIOR}`
