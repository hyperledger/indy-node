FROM docker.elastic.co/beats/filebeat:7.14.1
ENV ENV_NAME dev
ENV IP_ADDRESS "127.0.0.1"
ENV REDIS_HOST localhost
ENV REDIS_PORT 6379

USER root
ADD ./filebeat.yml /usr/share/filebeat/filebeat.yml
RUN chown root:filebeat /usr/share/filebeat/filebeat.yml && chmod go-w /usr/share/filebeat/filebeat.yml
USER filebeat

CMD ["filebeat", "-c", "filebeat.yml"]
