#!/usr/bin/env bash

#######################################################
# build-arg values for CI testing custom image builds #
#######################################################
# extra apt packages
export APT_PACKAGES="curl nano"
# extra version-pinned conda packages
export CONDA_PACKAGES="jupyterlab=2.1.5 pytest=5.4.3"
# older but recent pip version
export PIP_VERSION="20.2"
# extra pip packages (including a GitHub install)
export PIP_PACKAGES="nltools==0.4.2 git+https://github.com/ContextLab/supereeg.git@v0.2.1"
# alternate working directory
export WORKDIR="/myworkdir"
# alternate IP address for notebook server
# TODO: low priority: figure out how to test alternatives for this
# export NOTEBOOK_IP=
# alternate port for notebook server
export PORT=9876