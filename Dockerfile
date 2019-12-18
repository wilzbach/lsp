FROM            python:3.7-alpine

ENV             SENTRY_DSN https://bcd976c210e8458ab717fdea741c6a5a@sentry.io/1822749
ENV             STORYSCRIPT_HUB_API https://api.storyscript.io/graphql

RUN             mkdir /app
WORKDIR         /app
COPY            setup.py README.md sls.py /app/
COPY            sls/version.py /app/sls/version.py

RUN             python setup.py install

COPY            sls /app/sls

ENTRYPOINT      ["python", "/app/sls.py", "websocket"]
