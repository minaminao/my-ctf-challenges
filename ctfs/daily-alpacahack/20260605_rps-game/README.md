# Author's Writeup for RPS GAME

Daily AlpacaHack で 6/6 に出題した『RPS GAME』の作問者 Writeup です。

https://alpacahack.com/daily/challenges/rps-game

## 問題概要

問題文:
```
✊️️🖐️✌️
```

内容:
- サーバーと通信して 1000 回じゃんけんができます。
- 勝率 60 %、つまり 1000 回中 600 回以上勝てばフラグが貰えます。
- 普通にじゃんけんをしたら勝率 1/3 なのでどうしたらよいでしょうか。

サーバーで動いているスクリプト:
```python
import random

FLAG = "Alpaca{REDACTED}"
HANDS = ["r", "p", "s"]
ROUNDS = 1000
TARGET_WIN = int(ROUNDS * 0.6)

def shuffle(items):
    return sorted(items, key=lambda _: random.getrandbits(1))

print("ROCK PAPER SCISSORS GAME")
print(f"Win {TARGET_WIN} times in {ROUNDS} rounds.")
print("Hands: r / p / s")

win = 0
hands = HANDS[:]
for i in range(ROUNDS):
    hands = shuffle(hands)
    opponent = hands[0]
    you = input(f"Round {i+1} > ").strip()
    assert you in HANDS, "Invalid hand."
    result = (HANDS.index(you) - HANDS.index(opponent)) % 3
    win += (result == 1)

    print(f"Opponent: {opponent}, You: {you}")
    print(["Draw", "Win!", "Lose..."][result])
    print(f"Win count: {win}\n")

if win >= TARGET_WIN:
    print(f"Wow, you broke the game ... Flag: {FLAG}")
else:
    print("Leave the game.")
```

## 解法

相手のじゃんけんの手を決めるために `shuffle` という独自のシャッフル関数が使われています:
```python
def shuffle(items):
    return sorted(items, key=lambda _: random.getrandbits(1))
```

シャッフルした後の先頭の要素が相手の手になります。
勝率を 60 %以上にするためには、相手の手を予測する必要があります。

では、どうしたら予測できるでしょうか？

`random` モジュールは乱数生成器として Mersenne Twister を使います。
Mersenne Twister は十分な出力を観測すれば後続の結果を計算することが可能です。
なので、[過去の問題](https://alpacahack.com/daily/challenges/the-future-path) にもあったように、一見 `random.getrandbits(1)` を予測する方針を考えるかもしれません。

が、この問題では Mersenne Twister の乱数予測をする必要はありません。

実はシャッフルの結果に偏りがあります。
シャッフルの際、ランダムなキーでソートしていますが、キーは `0` または `1` の2通りです。
Python の `sorted` は安定ソートなので、同じキーになった要素同士は元の順序を保ちます。

例えば `[r, p, s]` のとき、各要素のキーと `shuffle([r, p, s])` の先頭の対応は、次のようになります。

| key(r) | key(p) | key(s) | sorted result | first |
| -----: | -----: | -----: | ------------- | ----- |
|      0 |      0 |      0 | `[r, p, s]`   | `r`   |
|      0 |      0 |      1 | `[r, p, s]`   | `r`   |
|      0 |      1 |      0 | `[r, s, p]`   | `r`   |
|      0 |      1 |      1 | `[r, p, s]`   | `r`   |
|      1 |      0 |      0 | `[p, s, r]`   | `p`   |
|      1 |      0 |      1 | `[p, r, s]`   | `p`   |
|      1 |      1 |      0 | `[s, r, p]`   | `s`   |
|      1 |      1 |      1 | `[r, p, s]`   | `r`   |

つまり、先頭 `r` が次も先頭に残る確率が `5/8`、つまり `62.5%` になります。

| first | count |   probability |
| ----- | ----: | ------------: |
| `r`   |     5 | `5/8 = 62.5%` |
| `p`   |     2 | `2/8 = 25.0%` |
| `s`   |     1 | `1/8 = 12.5%` |

したがって、直前の相手の手に勝つ手を出し続ければ、フラグを獲得できます。

Solver:
```python
from pwn import remote, args

ROUNDS = 1000

r = remote(args.HOST or "localhost", args.PORT or 1337, level="debug")

r.recvuntil(b"> ")
r.sendline(b"p")

for i in range(ROUNDS - 1):
    r.recvuntil(b"Opponent: ")
    opponent = r.recvuntil(b", You: ", drop=True).strip()

    if opponent == b"r":
        r.sendline(b"p")
    elif opponent == b"s":
        r.sendline(b"r")
    elif opponent == b"p":
        r.sendline(b"s")

r.recvall()
```

Flag: `Alpaca{Electrode Shuffle 0101}`

偏りのないシャッフルアルゴリズムは Fisher–Yates shuffle が有名です。
