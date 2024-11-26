all: generate-distfiles sync fmt lint type-check-strict

start-challenge-server:
	cd build && docker compose up --build

start-challenge-server-local:
	cd build && docker compose -f compose.development.yaml up --build

run-solver:
	cd solver && docker run -e CHALLENGE_HOST=trillion-ether.seccon.games -e CHALLENGE_PORT=31337 $$(docker build -q .)

run-solver-local:
	cd solver && docker run -e CHALLENGE_HOST=localhost -e CHALLENGE_PORT=31337 --network=host $$(docker build -q .)

PY_FILES = build/src/eth_sandbox/*.py build/src/deploy/*.py solver/*.py

build-contracts:
	cd build/src/contracts && forge build

generate-distfiles:
	rm -rf files 
	mkdir files
	cp build/src/contracts/src/TrillionEther.sol files/

sync:
	cp build/src/contracts/src/TrillionEther.sol solver/src/TrillionEther.sol

fmt:
	isort $(PY_FILES)
	ruff format $(PY_FILES)
	cd solver && forge fmt

lint:
	ruff check $(PY_FILES)

test-solver:
	cd solver && forge test

type-check:
	mypy $(PY_FILES) --ignore-missing-imports

type-check-strict:
	mypy $(PY_FILES) --strict --ignore-missing-imports
