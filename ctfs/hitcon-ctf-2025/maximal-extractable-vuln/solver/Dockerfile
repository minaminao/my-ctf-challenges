FROM ubuntu:24.04
WORKDIR /solver

RUN apt update -y && apt install curl git python3-pip python-is-python3 -y && apt upgrade -y
RUN pip install --break-system-packages pwntools

ENV SHELL=/bin/bash
RUN curl -L https://foundry.paradigm.xyz | bash
ENV PATH=$PATH:/root/.foundry/bin
RUN foundryup --install nightly

COPY . .

CMD ["python", "solve.py"]
