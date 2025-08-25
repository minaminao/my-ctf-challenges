The infra shouldn't be vulnerable.
It's not necessary to look at anywhere other than the contract files (`src/contracts`) to solve this challenge!

First, set the `FORKING_RPC_URL` in `compose.yaml` to your mainnet RPC endpoint (for example, Alchemy) to deploy the challenge contract on a network forked from the Ethereum mainnet.

Next, start the local challenge server:
```
docker compose up --build
```
