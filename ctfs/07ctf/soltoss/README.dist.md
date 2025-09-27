# soltoss

This challenge uses [otter-sec/sol-ctf-framework](https://github.com/otter-sec/sol-ctf-framework).
The `examples/` directory contains example challenges along with their solvers.

## Run

```
export DOCKER_DEFAULT_PLATFORM=linux/amd64 # if macOS
docker compose up --build
```

The challenge binaries has already been built.
If you want to modify the server and test them locally, use `docker compose -f compose.develop.yaml up --build` instead of the above command.
