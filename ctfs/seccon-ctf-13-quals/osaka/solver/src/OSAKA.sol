// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.26;

interface IGame {
    function play(address solverAddr) external;
}

interface IStickGameSolver {
    function solve(uint256 sticks) external returns (uint256);
}

contract StickGame is IGame {
    uint256 public initialSticks;

    constructor(uint256 initialSticks_) {
        initialSticks = initialSticks_;
    }

    function play(address solverAddr) external {
        uint256 sticks = initialSticks;
        for (uint256 i = 0; i < 100; i++) {
            uint256 solverInput = IStickGameSolver(solverAddr).solve(sticks);
            require(solverInput > 0 && solverInput <= 3, "Invalid input");
            sticks -= solverInput;
            if (sticks == 0) {
                // you win :)
                return;
            }
            uint256 computerInput = sticks % 4 == 0 ? 1 : sticks % 4;
            sticks -= computerInput;
            if (sticks == 0) {
                revert("Computer wins");
            }
        }
    }
}

contract ChronoGame is IGame {
    function play(address) external view {
        if (block.timestamp > 5000000000) {
            // you win :)
            return;
        } else {
            revert("Computer wins");
        }
    }
}

contract GameRegistry {
    mapping(address => mapping(uint256 => IGame)) public games;

    function registerGame(uint256 gameSlot, address gameAddr) external {
        games[msg.sender][gameSlot] = IGame(gameAddr);
    }
}

contract GameMaster {
    GameRegistry public gameRegistry;
    mapping(uint256 => uint256) public playCounts;

    constructor(GameRegistry gameRegistry_) {
        gameRegistry = gameRegistry_;
    }

    function initializeGame(uint256 gameId, uint256 parameter) external {
        uint256 gameSlot = gameId;
        if (gameId == 1) {
            gameRegistry.registerGame(gameSlot, address(new StickGame(parameter)));
        } else if (gameId == 2) {
            gameRegistry.registerGame(gameSlot, address(new ChronoGame()));
        }
    }

    function playGame(uint256 gameSlot, address challenger) external {
        IGame game = gameRegistry.games(address(this), gameSlot);
        playCounts[gameSlot]++;
        game.play(challenger);
    }
}

contract OSAKA {
    bool public isSolved;
    GameRegistry public gameRegistry;
    GameMaster public gameMaster;

    constructor() payable {
        gameRegistry = new GameRegistry();
        gameMaster = new GameMaster(gameRegistry);
    }

    function challenge() external {
        assembly {
            if eq(tload(0), true) { revert(0, 0) }
            tstore(0, true)

            let gameMasterAddr := sload(gameMaster.slot)
            let win := true

            // initialize games
            for { let i := 1 } lt(i, 3) { i := add(i, 1) } {
                mstore(0x40, 100)
                mstore(0x20, i)
                mstore(0x00, 0x9122b600)
                pop(extcall(gameMasterAddr, 0x1c, 0x44, 0))
            }

            // play games
            for { let i := 1 } lt(i, 3) { i := add(i, 1) } {
                mstore(0x40, caller())
                mstore(0x20, i)
                mstore(0x00, 0x3505b06f)
                let reverted := extcall(gameMasterAddr, 0x1c, 0x44, 0)
                if eq(reverted, true) { win := false }
            }

            // you need to win all games
            if eq(win, false) { revert(0, 0) }
            sstore(isSolved.slot, true)
        }
    }
}
