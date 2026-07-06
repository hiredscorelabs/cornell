FROM python:3.10

RUN pip install cornell

EXPOSE 9000

ENTRYPOINT ["cornell"]