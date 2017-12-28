FROM sovrincore

ARG ips
ARG nodecnt
ARG clicnt=10

ENV NODE_IP_LIST $ips
ENV NODE_COUNT $nodecnt
ENV CLIENT_COUNT $clicnt
ENV HOME=/home/sovrin

EXPOSE 5000-9799

COPY ./scripts/common/*.sh /home/sovrin/
COPY ./scripts/client/start.sh /home/sovrin/

RUN chown -R sovrin:root /home/sovrin && \
	chgrp -R 0 /home/sovrin && \
	chmod -R g+rwX /home/sovrin && \
	chmod +x /home/sovrin/*.sh

USER 10001
WORKDIR /home/sovrin
CMD ["/home/sovrin/start.sh"]