FROM indycore

ARG ips
ARG nodecnt
ARG clicnt=10

EXPOSE 5000-9799
USER indy
# Init pool data
RUN if [ ! -z "$ips" ] && [ ! -z "$nodecnt" ]; then generate_indy_pool_transactions --nodes $nodecnt --clients $clicnt --ips "$ips"; fi
CMD /bin/bash
