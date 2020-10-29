#!/usr/bin/env bash

DATE="$(date "+%Y%m%d%H%M")"
DOCKERFILE_DIR="./dockerfiles/"

# CUDA_COMPUTE_CAPABILITY => JETSON AGX XAVIER = 7.2, JETSON NANO = 5.3, JETSON TX2 = 6.2
if [[ $# -eq 1 && -n $1 ]]; then
  CUDA_COMPUTE_CAPABILITY=$1
else
  CUDA_COMPUTE_CAPABILITY="7.2"
fi

IMAGE_NAME="l4t-cupy-${CUDA_COMPUTE_CAPABILITY}"

docker build -f ${DOCKERFILE_DIR}/Dockerfile-pylib-cupy -t ${IMAGE_NAME}:"${DATE}" .
docker tag ${IMAGE_NAME}:"${DATE}" ${IMAGE_NAME}:latest
