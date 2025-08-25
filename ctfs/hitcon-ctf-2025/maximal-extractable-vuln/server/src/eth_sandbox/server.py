import json
import os
import random
import signal
import subprocess
import time
from threading import Thread
from uuid import uuid4

import requests
from eth_account.hdaccount import generate_mnemonic
from eth_sandbox.auth import get_shared_secret
from flask import Flask, Request, Response, request
from flask_cors import CORS, cross_origin
from web3 import Web3

app = Flask(__name__)
CORS(app)

ENV = os.getenv("ENV", "production")
NODE_KILL_AFTER_MINUTES = int(os.getenv("NODE_KILL_AFTER_MINUTES", "10"))
HTTP_PORT = os.getenv("HTTP_PORT", "8545")
FORKING_RPC_URL = os.getenv("FORKING_RPC_URL")
FORKING_BLOCK_NUMBER = os.getenv("FORKING_BLOCK_NUMBER")

if not FORKING_RPC_URL or not FORKING_RPC_URL.startswith("http"):
    raise RuntimeError("Environment variable FORKING_RPC_URL must be set")

if not FORKING_BLOCK_NUMBER:
    raise RuntimeError("Environment variable FORKING_BLOCK_NUMBER must be set")


try:
    os.mkdir("/tmp/instances-by-uuid")
except Exception:
    pass


def has_instance_by_uuid(uuid: str) -> bool:
    return os.path.exists(f"/tmp/instances-by-uuid/{uuid}")


def get_instance_by_uuid(uuid: str) -> dict:
    with open(f"/tmp/instances-by-uuid/{uuid}", "r") as f:
        return json.loads(f.read())


def delete_instance_info(node_info: dict) -> None:
    os.remove(f"/tmp/instances-by-uuid/{node_info['uuid']}")


def create_instance_info(node_info: dict) -> None:
    with open(f"/tmp/instances-by-uuid/{node_info['uuid']}", "w+") as f:
        f.write(json.dumps(node_info))


def really_kill_node(node_info: dict) -> None:
    print(f"killing node {node_info['uuid']}")

    delete_instance_info(node_info)

    os.kill(node_info["pid"], signal.SIGTERM)


def kill_node(node_info: dict) -> None:
    time.sleep(NODE_KILL_AFTER_MINUTES * 60)

    if not has_instance_by_uuid(node_info["uuid"]):
        return

    really_kill_node(node_info)


def launch_node() -> dict | None:
    assert FORKING_RPC_URL is not None and FORKING_BLOCK_NUMBER is not None

    port = random.randrange(30000, 60000)
    mnemonic = generate_mnemonic(12, "english")
    mnemonic_user = generate_mnemonic(12, "english")
    uuid = str(uuid4())

    anvil_command = [
        "/root/.foundry/bin/anvil",
        "--fork-url",
        FORKING_RPC_URL,
        "--fork-block-number",
        FORKING_BLOCK_NUMBER,
        "--accounts",
        "1",
        "--balance",
        "1100",
        "--mnemonic",
        mnemonic,
        "--port",
        str(port),
        "--block-base-fee-per-gas",
        "0",
    ]

    proc = subprocess.Popen(args=anvil_command)

    web3 = Web3(Web3.HTTPProvider(f"http://127.0.0.1:{port}"))
    while True:
        if proc.poll() is not None:
            return None
        if web3.is_connected():
            break
        time.sleep(0.1)

    node_info = {
        "port": port,
        "mnemonic": mnemonic,
        "mnemonic_user": mnemonic_user,
        "pid": proc.pid,
        "uuid": uuid,
    }

    reaper = Thread(target=kill_node, args=(node_info,))
    reaper.start()
    return node_info


def is_request_authenticated(request: Request) -> bool:
    token = request.headers.get("Authorization")

    return token == f"Bearer {get_shared_secret()}"


@app.route("/")
def index() -> str:
    return "sandbox is running!"


@app.route("/new", methods=["POST"])
@cross_origin()
def create() -> dict:
    if not is_request_authenticated(request):
        return {
            "ok": False,
            "error": "nice try",
        }

    print("launching node")

    node_info = launch_node()
    if node_info is None:
        print("failed to launch node")
        return {
            "ok": False,
            "error": "error_starting_chain",
            "message": "An error occurred while starting the chain",
        }
    create_instance_info(node_info)

    print(f"launched node (uuid={node_info['uuid']}, pid={node_info['pid']})")

    return {
        "ok": True,
        "uuid": node_info["uuid"],
        "mnemonic": node_info["mnemonic"],
        "mnemonic_user": node_info["mnemonic_user"],
    }


@app.route("/kill", methods=["POST"])
@cross_origin()
def kill() -> dict:
    if not is_request_authenticated(request):
        return {
            "ok": False,
            "error": "nice try",
        }

    body = request.get_json()

    uuid = body["uuid"]

    if not has_instance_by_uuid(uuid):
        print(f"no instance to kill for uuid {uuid}")
        return {
            "ok": False,
            "error": "not_running",
            "message": "No instance is running!",
        }

    really_kill_node(get_instance_by_uuid(uuid))

    return {
        "ok": True,
        "message": "Instance killed",
    }


ALLOWED_NAMESPACES = ["web3", "eth", "net"]
DISALLOWED_METHODS = [
    "eth_sign",
    "eth_signTransaction",
    "eth_signTypedData",
    "eth_signTypedData_v3",
    "eth_signTypedData_v4",
    "eth_sendTransaction",
    "eth_sendUnsignedTransaction",
]


@app.route("/<string:uuid>", methods=["POST"])
@cross_origin()
def proxy(uuid: str) -> str | dict | Response:
    body = request.get_json()
    if not body:
        return "invalid content type, only application/json is supported"

    if "id" not in body:
        return ""

    if not has_instance_by_uuid(uuid):
        return {
            "jsonrpc": "2.0",
            "id": body["id"],
            "error": {
                "code": -32602,
                "message": "invalid uuid specified",
            },
        }

    node_info = get_instance_by_uuid(uuid)

    if "method" not in body or not isinstance(body["method"], str):
        return {
            "jsonrpc": "2.0",
            "id": body["id"],
            "error": {
                "code": -32600,
                "message": "invalid request",
            },
        }

    prefix = f"/{uuid}:"

    print(f"{prefix} Method: {body['method']}")
    print(f"{prefix} Request body: {json.dumps(body, indent=2)}")
    print(f"{prefix} Headers: {dict(request.headers)}")

    ok = (
        any(body["method"].startswith(namespace) for namespace in ALLOWED_NAMESPACES)
        and body["method"] not in DISALLOWED_METHODS
    )
    if not ok and not is_request_authenticated(request):
        error_response = {
            "jsonrpc": "2.0",
            "id": body["id"],
            "error": {
                "code": -32600,
                "message": "forbidden jsonrpc method",
            },
        }
        print(f"{prefix} Response: {json.dumps(error_response, indent=2)}")
        print("---")
        return error_response

    resp = requests.post(f"http://127.0.0.1:{node_info['port']}", json=body)

    try:
        response_json = resp.json()
        print(f"{prefix} Response: {json.dumps(response_json, indent=2)}")
    except Exception as e:
        print(f"{prefix} Response (raw): {resp.text}")
        print(f"{prefix} JSON decode error: {e}")
    print(f"{prefix} Status code: {resp.status_code}")
    print("---")

    response = Response(resp.content, resp.status_code, resp.raw.headers.items())
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(HTTP_PORT))
