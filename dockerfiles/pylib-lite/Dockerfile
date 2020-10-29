# syntax = docker/dockerfile:experimental
FROM python:3.7-buster as builder

ADD dist .
ENV GRPC_PYTHON_BUILD_EXT_COMPILER_JOBS 8
RUN --mount=type=cache,target=/root/.cache/pip python3 -m pip install ./aion-0.0.1.tar.gz

FROM python:3.7-slim-buster as runner

RUN apt-get update -y && apt-get install -y \
    locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8

ENV AION_HOME=/var/lib/aion \
    LANG="ja_JP.UTF-8" \
    LANGUAGE="ja_JP:ja" \
    LC_ALL="ja_JP.UTF-8"

RUN mkdir ${AION_HOME}

COPY --from=builder /usr/local/lib/python3.7/site-packages /usr/local/lib/python3.7/site-packages
