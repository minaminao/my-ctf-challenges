start-challenge-server:
	cd server && docker compose up --build

start-challenge-server-local:
	cd distfiles && docker compose -f compose.yaml up --build

run-solver:
	cd solver && docker run -e CHALLENGE_HOST=mev.chal.hitconctf.com -e CHALLENGE_PORT=31337 $$(docker build -q .)

run-solver-local:
	cd solver && docker run -e CHALLENGE_HOST=localhost -e CHALLENGE_PORT=31337 --network=host $$(docker build -q .)
