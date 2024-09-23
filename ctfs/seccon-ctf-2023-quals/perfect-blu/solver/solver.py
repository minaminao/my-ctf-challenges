CALL_OBJECT_BYTECODE = bytes.fromhex("21820000" + "000000")  # CALL_OBJECT 000000??
KEY = "1234567890QWERTYUIOPASDFGHJKL{ZXCVBNM_-}"
PACKET_LEN = 192
PACKET_HEADER_LEN = 8
FLAG_LEN = 47

flag = ""

for flag_i in range(FLAG_LEN):
    m2ts = open(f"STREAM/{flag_i:05}.m2ts", "rb").read()
    stream = b"".join(
        [
            m2ts[i + PACKET_HEADER_LEN : i + PACKET_LEN]
            for i in range(0, len(m2ts), PACKET_LEN)
        ]
    )

    key_i = 0
    for i in range(len(stream)):
        if not stream[i : i + len(CALL_OBJECT_BYTECODE)] == CALL_OBJECT_BYTECODE:
            continue
        dst = stream[i + len(CALL_OBJECT_BYTECODE)]
        if dst == flag_i + 1:
            flag += KEY[key_i]
        key_i += 1

print(flag)
