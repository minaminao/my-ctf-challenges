# Author's Writeup for Substance

Daily AlpacaHack で 2/6 に出題した『The World』の作問者 Writeup です。

https://alpacahack.com/daily/challenges/the-world

## 問題概要

問題文:
```
時よ止まれ！
```

添付ファイルには次の Bash スクリプト `server.sh` が含まれており、サーバーで実行されています:
```bash
#!/bin/bash
set -euo pipefail
FLAG=${FLAG:-"Alpaca{*** REDACTED ***}"}

echo "[Warmup] current time (seconds)?"
read t; d1=$(( t-$(date +%s) ))
if (( -100 < d1 && d1 < 100 )); then
    echo "Well done."
else
    echo "Hm. diff: $d1"
    exit 1
fi

echo "[Impossible] current time (nanoseconds)?"
read t; d2=$(( t-$(date +%s%N) ))
if (( -100 < d2 && d2 < 100 )); then
    echo "The World! $FLAG"
else
    echo "Hm. diff: $d2"
    exit 1
fi
```

また、Dockerfile を読むと `bash:5.3.9` イメージがベースになっています。

スクリプトの挙動は、
- 現在時刻を秒単位で当てる（Warmup）
- 現在時刻をナノ秒単位で当てる（Impossible）

という2段階のゲームになっています。
両方のゲームを成功させるとフラグが表示されるようです。

しかし、ナノ秒精度での正確な入力は現実的ではないため、正攻法では難しいだろうと予想できます。

## 解法1

最も簡単な解法は、入力として `FLAG` を送ることです。

```
$ nc 34.170.146.252 23758
[Warmup] current time (seconds)?
FLAG
server.sh: line 6: Alpaca{muda.sh}: arithmetic syntax error: invalid arithmetic operator (error token is "{muda.sh}")
server.sh: line 7: d1: unbound variable
```

この解法には、次のような手順で、辿り着けると思います。

例えば、適当な文字列を入力してみると（ここでは例として `a`）、

```
$ nc 34.170.146.252 23758
[Warmup] current time (seconds)?
a
server.sh: line 6: a: unbound variable
```

「6行目で、未定義の変数 `a` を参照した」とエラーが出ます。

このことから、変数名を入力すると[算術展開でその変数を展開](https://www.gnu.org/software/bash/manual/bash.html#Arithmetic-Expansion-1)してくれそうなことがわかります。

`FLAG` は変数なので、 `FLAG` を試しに入力してみます。すると、フラグは文字列なので構文エラーが起き、フラグがエラーメッセージに出力されます。

## 解法2

解法1より難しいですが、実は `echo "The World! $FLAG"` に到達することも可能です。

先に答えを書くと、以下の手順でフラグを出力できます。

```
$ nc 34.170.146.252 23758
[Warmup] current time (seconds)?
(d2=0)+EPOCHSECONDS
Well done.
[Impossible] current time (nanoseconds)?
.
server.sh: line 15: .: arithmetic syntax error: operand expected (error token is ".")
The World! Alpaca{muda.sh}
```

まず、 `(d2=0)+EPOCHSECONDS` において、算術展開内で `d2` を `0` に代入しています。この代入の効果は後々使います。

`(d2=0)` は `0` なので、それに `EPOCHSECONDS` が足されます。
`EPOCHSECONDS` は Bash 5.0 で追加された環境変数で、現在時刻の秒数を返します。`EPOCHSECONDS` を使うのは必須ではなく、具体的な現在時刻を数値として入力しても問題ありません。

これにより、`d1` は `0` になり、 Warmup はクリアできます。

Impossible では、 構文エラーを起こすために `.` を入力しています。
構文エラーを起こせるなら `.` 以外の記号でも構いません。

`set -e` があってエラーが起きているのに、次の行に処理が進むのは意外に思うかもしれませんが、 `set -e` では算術展開時の `arithmetic syntax error` は対象外です。

構文エラーにより `d2` への代入は失敗します。しかし、Warmup 時に `d2` に `0` を既に代入しているので `d2: unbound variable` エラーにならず、 `-100 < d2 && d2 < 100` の条件を満たすことができます。結果、フラグが出力されます。

ちなみに [Bashのソースコード](https://cgit.git.savannah.gnu.org/cgit/bash.git/tree/subst.c?h=bash-5.3&id=b8c60bc9ca365f8261fa97900b6fa939f6ebc303#n10874) を読むと `set -o posix` をつけると算術展開時のこのようなエラーを即時終了するように対処できることがわかります。

Flag: `Alpaca{muda.sh}`
