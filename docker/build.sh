#!/bin/bash

REPO_ROOT=$(git rev-parse --show-toplevel)
docker build $REPO_ROOT \
    --build-arg UID=$(id -u) \
    --build-arg GID=$(id -g) \
    --build-arg UNAME=pra-$(id -un) \
    --rm -t pra-$(id -un) -f $REPO_ROOT/docker/Dockerfile
