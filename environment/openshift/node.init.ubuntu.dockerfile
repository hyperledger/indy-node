# Development
FROM indycore

ARG nodename
ARG nport
ARG cport
ARG ips
ARG nodenum
ARG nodecnt
ARG clicnt=10

ENV NODE_NUMBER $nodenum
ENV NODE_NAME $nodename
ENV NODE_PORT $nport
ENV CLIENT_PORT $cport
ENV NODE_IP_LIST $ips
ENV NODE_COUNT $nodecnt
ENV CLIENT_COUNT $clicnt
ENV HOME=/home/indy
ENV TEST_MODE=
ENV HOLD_EXT="indy "

EXPOSE $nport $cport

COPY ./scripts/common/*.sh /home/indy/
COPY ./scripts/node/start.sh /home/indy/

RUN chown -R indy:root /home/indy && \
	chgrp -R 0 /home/indy && \
	chmod -R g+rwX /home/indy && \
	chmod +x /home/indy/*.sh

USER 10001
WORKDIR /home/indy
CMD ["/home/indy/start.sh"]
