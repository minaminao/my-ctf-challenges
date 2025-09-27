FROM ubuntu:24.04
COPY --from=krallin/ubuntu-tini /usr/bin/tini /tini
ENTRYPOINT ["/tini", "--"]

RUN apt-get update && \
    apt-get -y install libudev-dev libssl-dev pkg-config && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY soltoss-server soltoss.so flag.txt /app/

RUN chown nobody:nogroup /app

EXPOSE 5001
USER nobody
CMD ["/app/soltoss-server"]
