FROM python:3.11.9

RUN true \
    && mkdir /var/log/ctf /startup \
    && apt update \
    && apt install -y xinetd tini \
    && rm -rf /var/cache/apt/archives \
    && useradd -m ctf \
    && true

COPY 00-create-xinetd-service /startup
COPY 99-start-xinetd /startup
COPY handler.sh /home/ctf/handler.sh
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /home/ctf/handler.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["tini", "-g", "--"]
CMD ["/entrypoint.sh"]

RUN true \
    && curl -L https://foundry.paradigm.xyz | bash \
    && bash -c "source /root/.bashrc && foundryup" \
    && chmod 755 -R /root \
    && true

COPY 98-start-gunicorn /startup

ENV PYTHONPATH /usr/lib/python

COPY requirements.txt /root

RUN python3 -m pip install -r /root/requirements.txt 

COPY deploy/ /home/ctf/

COPY contracts/out /home/ctf/compiled

COPY eth_sandbox /usr/lib/python/eth_sandbox
