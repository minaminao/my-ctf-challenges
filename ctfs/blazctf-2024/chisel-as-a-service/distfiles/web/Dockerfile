FROM node:22.7.0-slim

WORKDIR /app

RUN apt update && apt install -y curl git

COPY package.json package-lock.json ./
RUN npm install

RUN curl -L https://foundry.paradigm.xyz | bash \
    && bash -c "source /root/.bashrc && foundryup"
RUN chmod 755 -R /root
ENV PATH="/root/.foundry/bin:${PATH}"
RUN mkdir /.svm && chmod 1777 /.svm

COPY . .

RUN mv flag.txt /flag-$(md5sum flag.txt | cut -c-32).txt
RUN chmod 1777 public/out

USER 404:404
# To install Solidity
RUN chisel
CMD node index.js
