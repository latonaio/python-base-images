#!/usr/bin/env bash

PUSH=$1
DATE="$(date "+%Y%m%d%H%M")"
REPOSITORY_PREFIX="latonaio"
SERVICE_NAME="pylib-python3"
DOCKERFILE_DIR="./dockerfiles/"

DOCKER_BUILDKIT=1 docker build --progress=plain -f ${DOCKERFILE_DIR}/Dockerfile-pylib-python3 -t ${SERVICE_NAME}:"${DATE}" .
# tagging
docker tag ${SERVICE_NAME}:"${DATE}" ${SERVICE_NAME}:latest
docker tag ${SERVICE_NAME}:"${DATE}" ${REPOSITORY_PREFIX}/${SERVICE_NAME}:"${DATE}"
docker tag ${REPOSITORY_PREFIX}/${SERVICE_NAME}:"${DATE}" ${REPOSITORY_PREFIX}/${SERVICE_NAME}:latest

if [[ $PUSH == "push" ]]; then
    docker push ${REPOSITORY_PREFIX}/${SERVICE_NAME}:"${DATE}"
    docker push ${REPOSITORY_PREFIX}/${SERVICE_NAME}:latest
fi

