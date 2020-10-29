#!/usr/bin/env bash

PUSH=$1
DATE="$(date "+%Y%m%d%H%M")"
REPOSITORY_PREFIX="latonaio"
SERVICE_NAME="l4t-ds-ffmpeg"
DOCKERFILE_DIR="./dockerfiles/pylib-ds-ffmpeg"

# build servicebroker
docker build --progress=plain -f ${DOCKERFILE_DIR}/Dockerfile -t ${SERVICE_NAME}:"${DATE}" .
# tagging
docker tag ${SERVICE_NAME}:"${DATE}" ${SERVICE_NAME}:latest
docker tag ${SERVICE_NAME}:"${DATE}" ${REPOSITORY_PREFIX}/${SERVICE_NAME}:"${DATE}"
docker tag ${REPOSITORY_PREFIX}/${SERVICE_NAME}:"${DATE}" ${REPOSITORY_PREFIX}/${SERVICE_NAME}:latest

if [[ $PUSH == "push" ]]; then
    docker push ${REPOSITORY_PREFIX}/${SERVICE_NAME}:"${DATE}"
    docker push ${REPOSITORY_PREFIX}/${SERVICE_NAME}:latest
fi
