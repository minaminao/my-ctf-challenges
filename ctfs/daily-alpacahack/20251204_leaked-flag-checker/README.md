# Writeup for Leaked Flag Checker

## 概要
https://alpacahack.com/daily/challenges/leaked-flag-checker

バイナリ `challenge` とそのソースコード `challenge.c` が与えられます。

`challenge.c`:
```c
// gcc -o challenge challenge.c
#include <stdio.h>
#include <string.h>

int main(void) {
    char input[32];
    const char xor_flag[] = "REDACTED";
    size_t flag_len = strlen(xor_flag);

    printf("Enter flag: ");
    fflush(stdout);
    scanf("%31s", input);

    if(strlen(input) != flag_len) {
        printf("Wrong length\n");
        return 1;
    }
    for(size_t i = 0; i < flag_len; i++) {
        if((input[i] ^ 7) != xor_flag[i]) {
            printf("Wrong at index %zu\n", i);
            return 1;
        }
    }
    printf("Correct\n");
    return 0;
}
```

ただし、ソースコード上は `xor_flag` は `REDACTED` になっており隠されています。

ソースコードを読むと、ユーザーの入力が `input` に格納され、プログラムは以下の処理を行います:
1. 文字列長を比較。
2. 各文字を `7` で XOR して比較。間違えたインデックスの場所を出力。


また、バイナリを `file` コマンドにかけた結果は以下です:
```
$ file challenge
challenge: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=5d2c86ed744df49647f3bd9cee8cfc4a90041315, for GNU/Linux 3.2.0, not stripped
```

## 解法1

`REDACTED` の値がわかりさえすれば、その値に `7` を XOR するだけでフラグが求まるので、まずは `REDACTED` の値を取得することを目指します。

そのために Binary Ninja や Ghidra などのバイナリ解析ツールで `challenge` を読み込んでみます。

今回は Binary Ninja を使ってみると、`main` 関数は次のような結果になります:

![alt text](assets/image.png)

この結果とソースコードと照らし合わせると `Fkwfdf|krdl~z` が怪しそうです。

Python で逆算してみると、

```
$ python
>>> "".join([chr(ord(c) ^ 7) for c in "Fkwfdf|krdl~z"])
'Alpaca{lucky}'
```

フラグが求まりました。

Flag: `Alpaca{lucky}`

## 解法2

バイナリ解析ツールを使わなくても、この問題は解くことができます。

バイナリの出力結果からフラグを特定していけるからです。

まず、フラグ長を絞ります。適当にフラグの長さを伸ばしていくと、

```
$ ./challenge 
Enter flag: Alpaca{AAAA} 
Wrong length

$ ./challenge 
Enter flag: Alpaca{AAAAA}
Wrong at index 7
```

このようになり、フラグの長さが13文字だとわかります。

次に、括弧内の文字を特定していきます。

間違っているインデックスを出力してくれるので、それをもとに一文字ずつ特定するPythonスクリプトを書けばよいです:

```python
import subprocess
import string


flag_prefix = "Alpaca{"
flag_middle = ""
flag_suffix = "}"

for i in range(5):
    for c in string.printable:
        flag = flag_prefix + flag_middle + c + "A" * (4 - i) + flag_suffix
        print("check: " + flag)
        result = subprocess.run(
            ["./challenge"], input=flag + "\n", capture_output=True, text=True
        )
        if result.returncode == 0:
            print("found flag: " + flag)
            exit()
        wrong_index = int(result.stdout.split()[-1])
        if wrong_index > i + 7:
            flag_middle += c
            break
```

これを実行してみると:

```
$ python solve.py
check: Alpaca{0AAAA}
check: Alpaca{1AAAA}
check: Alpaca{2AAAA}
check: Alpaca{3AAAA}
check: Alpaca{4AAAA}
...
check: Alpaca{luckk}
check: Alpaca{luckl}
check: Alpaca{luckm}
check: Alpaca{luckn}
check: Alpaca{lucko}
check: Alpaca{luckp}
check: Alpaca{luckq}
check: Alpaca{luckr}
check: Alpaca{lucks}
check: Alpaca{luckt}
check: Alpaca{lucku}
check: Alpaca{luckv}
check: Alpaca{luckw}
check: Alpaca{luckx}
check: Alpaca{lucky}
found flag: Alpaca{lucky}
```

となり、フラグが求まります。
