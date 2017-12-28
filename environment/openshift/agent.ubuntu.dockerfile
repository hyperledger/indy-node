FROM sovrincore

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
ENV HOME=/home/sovrin

EXPOSE $agentport

COPY ./scripts/common/*.sh /home/sovrin/
COPY ./scripts/agent/start.sh /home/sovrin/

RUN chown -R sovrin:root /home/sovrin && \
	chgrp -R 0 /home/sovrin && \
	chmod -R g+rwX /home/sovrin && \
	chmod +x /home/sovrin/*.sh

USER 10001
WORKDIR /home/sovrin
CMD ["/home/sovrin/start.sh"]