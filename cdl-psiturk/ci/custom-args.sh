#!/usr/bin/env bash

#######################################################
# build-arg values for CI testing custom image builds #
#######################################################
# extra apt packages
export APT_PACKAGES="curl htop"
# extra version-pinned conda packages
export CONDA_PACKAGES="numpy=1.19.1 requests=2.24.0"
# older but recent pip version
export PIP_VERSION="20.0.2"
# extra pip packages (including a GitHub install)
export PIP_PACKAGES="quail==0.2.0 git+https://github.com/ContextLab/hypertools.git@3f45375682a8f12a1278dd1720290d75a50062a9"
# alternate working directory
export WORKDIR="/myworkdir"
# build for use with MTurk
export MTURK=true