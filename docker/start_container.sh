#!/bin/bash
REPO_ROOT=$(git rev-parse --show-toplevel)
docker run -it \
    --name pra-$(id -un) \
    --env TERM=xterm-256color \
    --user $(id -u):$(id -g) \
    --volume $REPO_ROOT:/workspace/PeerReviewAgent \
    --volume $HOME/.gitconfig:/home/pra-$(id -un)/.gitconfig \
    --ipc=host \
    --network host \
    --shm-size=512g \
    pra-$(id -un) sh -c "pre-commit install -f && zsh"
