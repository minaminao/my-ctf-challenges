# Author's Writeup for Flag Printer 2026

Daily AlpacaHack で 3/4 に出題した『Flag Printer 2026』の作問者 Writeup です。

https://alpacahack.com/daily/challenges/flag-printer-2026

## 問題概要

問題文:
```
フ〜〜〜〜〜〜〜〜〜〜ラ〜〜〜〜〜〜〜〜〜〜グ〜〜〜〜〜〜〜〜〜〜
```

配布ファイルを読むと、次の Python スクリプトがサーバーで実行されていることがわかります:
```python
import time

flag = "Alpaca{????}"
assert len(flag) == 12

for i, c in enumerate(flag):
    print(c, end="", flush=True)
    time.sleep(i)
```

フラグの `i` 文字目が出力されるごとに `i` 秒 sleep しています。

ただ待つだけでフラグが表示されそうですが、実際には `Alpaca{` 以降が出力されません:

```
$ nc 34.170.146.252 10951
Alpaca{
```

## 解法

この挙動は不備ではありません。

配布されている `Dockerfile` を読むと、

```Dockerfile
FROM python:3.14.3
WORKDIR /app
RUN apt-get update && apt-get install -yq socat
COPY server.py .

CMD ["socat", "-T5", "tcp-listen:1337,fork,reuseaddr", "exec:'python server.py'"]
```

`python server.py` の実行に `socat` で接続できるようになっています。

ここでオプションで `-T5` を渡していますが、これは5秒通信がないと接続を切るという意味です。

つまり、 `nc` でサーバーに接続して、`{` が出力されてから5秒通信がなかったため接続が切れていたわけです。

なので、接続が切れないように適当な文字を送信していればフラグの続きが得られます。

適当に `!` を送り続けると、
```
$ nc 34.170.146.252 10951
Alpaca{!
c!
u!
t!
!
3!
!
}
```

フラグが得られました。

Flag: `Alpaca{cut3}`

CTF では `Dockerfile` にフラグの場所など重要な情報が示されていることが多いので（`flag.txt` か `flag-[md5sum].txt` か、など）、軽く目を通すのがおすすめです。
