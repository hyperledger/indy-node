FROM docker.elastic.co/beats/metricbeat:7.14.1
ENV IP_ADDRESS "127.0.0.1"
ENV REDIS_HOST localhost
ENV REDIS_PORT 6379

USER root
ADD ./metricbeat.yml /usr/share/metricbeat/metricbeat.yml
RUN chown root:metricbeat /usr/share/metricbeat/metricbeat.yml && chmod go-w /usr/share/metricbeat/metricbeat.yml
USER metricbeat

CMD ["metricbeat", "-c", "metricbeat.yml"]
