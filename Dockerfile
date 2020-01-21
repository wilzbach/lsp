# first stage
FROM            alpine:3.10 as version
RUN             apk --no-cache add python3 git
RUN             mkdir /app
WORKDIR         /app
ADD             .git /app/.git
ADD             setup.py README.md /app/
RUN             python3 setup.py egg_info
RUN             ls -l sls.egg-info

FROM            alpine:3.10

ENV             SENTRY_DSN https://bcd976c210e8458ab717fdea741c6a5a@sentry.io/1822749
ENV             STORYSCRIPT_HUB_API https://api.storyscript.io/graphql

RUN             mkdir /app
WORKDIR         /app
COPY            setup.py README.md sls.py /app/
COPY            --from=version /app/sls.egg-info /app/

# Required for tornado.speedups
RUN             apk --no-cache add build-base python3 python3-dev sqlite-dev && \
                python3 setup.py install && \
                apk del build-base python3-dev sqlite-dev

COPY            sls /app/sls

ENTRYPOINT      ["python3", "/app/sls.py", "websocket"]
