from pathlib import Path

import eth_sandbox
import eth_sandbox.launcher
from eth_typing import HexStr
from web3 import Web3
from web3.types import Wei


def deploy(web3: Web3, deployer_address: str, player_address: str) -> str:
    receipt = eth_sandbox.launcher.send_transaction(
        web3,
        {
            "from": deployer_address,
            "data": HexStr(
                Path("compiled/land_of_the_lustrous.bin").read_text().strip()
            ),
            "value": Wei(1_000_000 * 10**18),
        },
    )
    assert receipt is not None
    challenge_addr = receipt["contractAddress"]
    assert challenge_addr is not None

    eth_sandbox.launcher.send_transaction(
        web3,
        {"from": deployer_address, "to": player_address, "value": 15 * 10 ** (18 - 1)},
    )

    return challenge_addr


eth_sandbox.launcher.run_launcher(
    [
        eth_sandbox.launcher.new_launch_instance_action(deploy),
        eth_sandbox.launcher.new_kill_instance_action(),
        eth_sandbox.launcher.new_battle_action(),
        eth_sandbox.launcher.new_get_flag_action(),
    ]
)
