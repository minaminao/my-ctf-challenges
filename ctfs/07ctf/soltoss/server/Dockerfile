FROM ubuntu:24.04 AS builder

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    pkg-config \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /app

COPY ./program/ /app/program/
COPY ./server/ /app/server/

WORKDIR /app/server

RUN cargo build --release

RUN mkdir -p /output && \
    cp ./target/release/soltoss-server /output/

CMD ["sh", "-c", "cp /app/server/target/release/soltoss-server /output/"]
