FROM debian

RUN apt-get update && apt-get install -y cron curl && rm -rf /var/lib/apt/lists/*

COPY crontab.txt /etc/cron.d/ingestor-cron
RUN chmod 0644 /etc/cron.d/ingestor-cron && crontab /etc/cron.d/ingestor-cron

RUN touch /var/log/cron.log

CMD ["cron", "-f"]
