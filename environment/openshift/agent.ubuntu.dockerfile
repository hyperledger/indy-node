FROM indycore

ARG ips
ARG nodecnt
ARG clicnt=10
ARG agentname
ARG agentport

ENV NODE_IP_LIST $ips
ENV NODE_COUNT $nodecnt
ENV CLIENT_COUNT $clicnt
ENV AGENT_NAME $agentname
ENV AGENT_PORT $agentport
ENV HOME=/home/indy

EXPOSE $agentport

COPY ./scripts/common/*.sh /home/indy/
COPY ./scripts/agent/start.sh /home/indy/

RUN chown -R indy:root /home/indy && \
	chgrp -R 0 /home/indy && \
	chmod -R g+rwX /home/indy && \
	chmod +x /home/indy/*.sh

USER 10001
WORKDIR /home/indy
CMD ["/home/indy/start.sh"]