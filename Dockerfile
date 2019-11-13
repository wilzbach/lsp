FROM            python:3.7-alpine

RUN             mkdir /app
WORKDIR         /app
COPY            setup.py README.md sls.py /app/
COPY            sls/version.py /app/sls/version.py

RUN             python setup.py install

COPY            sls /app/sls

ENTRYPOINT      ["python", "/app/sls.py", "websocket"]
