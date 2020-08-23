# should rarely be changed, but could substitute a different linux distro:version
ARG BASE_IMAGE=debian:stretch
FROM $BASE_IMAGE

LABEL maintainer="Paxton Fitzpatrick <paxton.c.fitzpatrick@dartmouth.edu>"

# (like setting via ENV, but doesn't persist after build)
ARG DEBIAN_FRONTEND=noninteractive

# set locale
ENV LANG C.UTF-8

# uncomment line in skeleton .bashrc to enable terminal colors, install basic apt packages
RUN sed -i 's/^#force_color_prompt=yes/force_color_prompt=yes/' /etc/skel/.bashrc && \
    apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends eatmydata && \
    eatmydata apt-get install -y --no-install-recommends \
    ca-certificates \
    mpich \
    procps \
    sudo \
    vim \
    wget \
 && rm -rf /var/lib/apt/lists/*
