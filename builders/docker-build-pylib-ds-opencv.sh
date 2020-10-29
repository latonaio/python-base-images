#!/usr/bin/env bash

DATE="$(date "+%Y%m%d%H%M")"
DOCKERFILE_DIR="./dockerfiles/"

# CUDA_COMPUTE_CAPABILITY => JETSON AGX XAVIER = 7.2, JETSON NANO = 5.3, JETSON TX2 = 6.2
if [[ $# -eq 1 && -n $1 ]]; then
    CUDA_COMPUTE_CAPABILITY=$1
else
    CUDA_COMPUTE_CAPABILITY="7.2"
fi

PUSH=$2
REPOSITORY_PREFIX="latonaio"
SERVICE_NAME="l4t-ds-opencv-${CUDA_COMPUTE_CAPABILITY}"

# build servicebroker
DOCKER_BUILDKIT=0 docker build --progress=plain -f ${DOCKERFILE_DIR}/Dockerfile-pylib-ds-opencv -t ${SERVICE_NAME}:"${DATE}" \
    --build-arg CUDA_COMPUTE_CAPABILITY=${CUDA_COMPUTE_CAPABILITY} .
# tagging
docker tag ${SERVICE_NAME}:"${DATE}" ${SERVICE_NAME}:latest
docker tag ${SERVICE_NAME}:"${DATE}" ${REPOSITORY_PREFIX}/${SERVICE_NAME}:"${DATE}"
docker tag ${REPOSITORY_PREFIX}/${SERVICE_NAME}:"${DATE}" ${REPOSITORY_PREFIX}/${SERVICE_NAME}:latest

if [[ $PUSH == "true" ]]; then
    docker push ${REPOSITORY_PREFIX}/${SERVICE_NAME}:"${DATE}"
    docker push ${REPOSITORY_PREFIX}/${SERVICE_NAME}:latest
fi
