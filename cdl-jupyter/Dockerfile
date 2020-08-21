FROM contextlab/cdl-python
LABEL maintainer="Paxton Fitzpatrick <paxton.c.fitzpatrick@dartmouth.edu>"

# define other build-time variables
ARG APT_PACKAGES=""
ARG PYTHON_VERSION=default
ARG CONDA_PACKAGES=""
ARG PIP_VERSION=default
ARG PIP_PACKAGES=""
ARG WORKDIR="/mnt"
ARG PORT=9999

# combine a bunch of conditional commands (install additional apt packages,
# update Python version, update pip, install additional Python packages) with
# definite install of Jupyter/SciPy-related packages to avoid caching intermediates
RUN if [ ! -z $APT_PACKAGES ]; then { apt-get update --fix-missing eatmydata && \
                                      apt-get install -y $APT_PACKAGES && \
                                      rm -rf /var/lib/apt/lists/* }; fi && \
    if [ ! $PYTHON_VERSION = default ]; then { echo "installing Python=${PYTHON_VERSION}" && \
                                               conda install --yes python=$PYTHON_VERSION }; fi
    conda update setuptools && \
    conda install -y notebook=6.1.3 \
    $CONDA_PACKAGES && \
    if [ ! $PIP_VERSION = 'default' ]; then pip install -y pip=$PIP_VERSION; fi && \
    if [ ! -z $PIP_PACKAGES ]; then pip install $PIP_PACKAGES; fi
