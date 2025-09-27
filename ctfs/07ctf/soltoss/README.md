# soltoss

**Challenge Name**:  
soltoss

**Description**:  
```
What's your favorite thing to toss in your ramen?

{{ nc }}

NOTE: Make sure it can be solved locally before running it remotely.
```

## Run

```
export DOCKER_DEFAULT_PLATFORM=linux/amd64 # if macOS
docker compose --build
```

## Build & Run

```
export DOCKER_DEFAULT_PLATFORM=linux/amd64 # if macOS
docker compose -f compose.develop.yaml up --build
```

## Format

```
make fmt
```

## Generate Distfiles

```
make generate-distfiles
```
