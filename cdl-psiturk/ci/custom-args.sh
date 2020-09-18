#!/usr/bin/env bash

#######################################################
# build-arg values for CI testing custom image builds #
#######################################################
# extra apt packages
export APT_PACKAGES="curl htop"
# extra version-pinned conda packages
export CONDA_PACKAGES="numpy=1.19.1 requests=2.24.0"
# older but recent pip version
export PIP_VERSION="19.3.1"
# extra pip packages (including a GitHub install)
export PIP_PACKAGES="quail==0.2.0 git+https://github.com/ContextLab/hypertools.git@dea0df127b150c39ed9a7b1faaa8fbde089ee834"
# alternate working directory
export WORKDIR="/myworkdir"
# build for use with MTurk
export MTURK=true