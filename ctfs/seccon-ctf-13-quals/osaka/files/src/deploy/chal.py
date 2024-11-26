import json
from pathlib import Path

import eth_sandbox
import eth_sandbox.launcher
from web3 import Web3


def deploy(web3: Web3, deployer_address: str, player_address: str) -> str:
    receipt = eth_sandbox.launcher.send_transaction(
        web3,
        {
            "from": deployer_address,
            "data": json.loads(Path("compiled/OSAKA.sol/OSAKA.json").read_text())[
                "bytecode"
            ]["object"],
        },
        ignore_status=True,  # NOTE: to resolve an anvil bug
    )
    assert receipt is not None
    challenge_addr = receipt["contractAddress"]
    assert challenge_addr is not None

    eth_sandbox.launcher.send_transaction(
        web3,
        {"from": deployer_address, "to": player_address, "value": 10**18},
    )

    return challenge_addr


eth_sandbox.launcher.run_launcher(
    [
        eth_sandbox.launcher.new_launch_instance_action(deploy),
        eth_sandbox.launcher.new_kill_instance_action(),
        eth_sandbox.launcher.new_get_flag_action(),
    ]
)
