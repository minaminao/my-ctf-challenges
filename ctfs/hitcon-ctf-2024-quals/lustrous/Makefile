all: generate-distfiles sync fmt lint test-solver type-check-strict

start-challenge-server:
	cd server && docker compose up --build

start-dist-challenge-server:
	cd distfiles && docker compose up --build

start-challenge-server-dev:
	cd server && docker compose -f compose.development.yaml up --build

run-solver:
	cd solver && docker run -e CHALLENGE_HOST=localhost -e CHALLENGE_PORT=31337 --network=host $$(docker build -q .)

run-solver-remote:
	cd solver && docker run -e CHALLENGE_HOST=lustrous.chal.hitconctf.com -e CHALLENGE_PORT=31337 $$(docker build -q .)

PY_FILES = server/src/eth_sandbox/*.py server/src/deploy/*.py solver/*.py

generate-distfiles:
	rm -rf distfiles
	cp -r server distfiles
	rm distfiles/compose.yaml
	mv distfiles/compose.development.yaml distfiles/compose.yaml
	sed -i 's/FLAG=hitcon{[^}]*}/FLAG=hitcon{redacted}/g' distfiles/compose.yaml
	sed -i 's/SHARED_SECRET=.*/SHARED_SECRET=redactedredacted/g' distfiles/compose.yaml
	tar -czf distfiles.tar.gz distfiles

sync:
	cp server/src/contracts/land_of_the_lustrous.vy solver/src/challenge/land_of_the_lustrous.vy

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
