#!/usr/bin/env bash

DATE="$(date "+%Y%m%d%H%M")"
DOCKERFILE_DIR="./dockerfiles/"
IMAGE_NAME="l4t-ds-opencv"

# build servicebroker
docker build -f ${DOCKERFILE_DIR}/Dockerfile-tmp-pylib-ds-opencv -t ${IMAGE_NAME}:"${DATE}" .
docker tag ${IMAGE_NAME}:"${DATE}" ${IMAGE_NAME}:latest
