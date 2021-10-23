FROM python:3

RUN pip install cornell

EXPOSE 9000

ENTRYPOINT ["cornell"]