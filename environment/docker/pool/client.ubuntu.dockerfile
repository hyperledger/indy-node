FROM indycore

ARG ips
ARG nodecnt
ARG clicnt=10

EXPOSE 5000-9799
USER indy

# Set NETWORK_NAME in indy_config.py to 'sandbox'
RUN awk '{if (index($1, "NETWORK_NAME") != 0) {print("NETWORK_NAME = \"sandbox\"")} else print($0)}' /etc/indy/indy_config.py> /tmp/indy_config.py
RUN mv /tmp/indy_config.py /etc/indy/indy_config.py


# Init pool data
RUN if [ ! -z "$ips" ] && [ ! -z "$nodecnt" ]; then generate_indy_pool_transactions --nodes $nodecnt --clients $clicnt --ips "$ips"; fi

CMD /bin/bash
