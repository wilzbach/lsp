FROM            alpine:3

ENV             SENTRY_DSN https://bcd976c210e8458ab717fdea741c6a5a@sentry.io/1822749
ENV             STORYSCRIPT_HUB_API https://api.storyscript.io/graphql

RUN             mkdir /app
WORKDIR         /app
COPY            setup.py README.md sls.py sls.egg-info /app/

# Required for tornado.speedups
RUN             apk --no-cache add build-base python3 python3-dev sqlite-dev && \
                python3 setup.py install && \
                apk del build-base python3-dev sqlite-dev

COPY            sls /app/sls

ENTRYPOINT      ["python3", "/app/sls.py", "websocket"]
