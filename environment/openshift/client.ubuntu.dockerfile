FROM indycore

ARG ips
ARG nodecnt
ARG clicnt=10

ENV NODE_IP_LIST $ips
ENV NODE_COUNT $nodecnt
ENV CLIENT_COUNT $clicnt
ENV HOME=/home/indy

EXPOSE 5000-9799

COPY ./scripts/common/*.sh /home/indy/
COPY ./scripts/client/start.sh /home/indy/

RUN chown -R indy:root /home/indy && \
	chgrp -R 0 /home/indy && \
	chmod -R g+rwX /home/indy && \
	chmod +x /home/indy/*.sh

USER 10001
WORKDIR /home/indy
CMD ["/home/indy/start.sh"]