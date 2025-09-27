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

RUN curl --proto '=https' --tlsv1.2 -sSfL https://solana-install.solana.workers.dev | bash
ENV PATH="/root/.local/share/solana/install/active_release/bin:$PATH"

WORKDIR /app

COPY ./program/Cargo.toml ./
COPY ./program/src/ ./src/

RUN cargo build-sbf

RUN mkdir -p /output && \
    cp ./target/deploy/soltoss.so /output/

CMD ["sh", "-c", "cp /app/target/deploy/soltoss.so /output/"]
