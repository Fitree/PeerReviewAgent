FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04

ADD . /workspace/PeerReviewAgent
WORKDIR /workspace/PeerReviewAgent

RUN apt update && apt upgrade -y
RUN apt install -y git wget curl vim zsh tmux python3 python3-pip
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -e .

ARG UNAME
ARG UID
ARG GID
RUN groupadd -g $GID -o $UNAME
RUN useradd -m -u $UID -g $GID -o -s /bin/bash $UNAME
USER $UNAME

RUN python -c "$(curl -fsSL https://raw.githubusercontent.com/Fitree/dev-env-setup/refs/heads/main/scripts/autosetup.py)"
