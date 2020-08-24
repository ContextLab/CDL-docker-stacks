FROM contextlab/cdl-base

LABEL maintainer="Paxton Fitzpatrick <paxton.c.fitzpatrick@dartmouth.edu>"

# define build-time variables
ARG APT_PACKAGES=""
ARG PYTHON_VERSION=3.8
ARG CONDA_PACKAGES=""
ARG PIP_VERSION=""
ARG PIP_PACKAGES=""
ARG WORKDIR="/mnt"

# add conda executable to path
ENV PATH /opt/conda/bin:$PATH

# Install miniconda & any additional apt packages
RUN if [ ! -z $APT_PACKAGES ]; then \
        apt-get update --fix-missing \
        && eatmydata apt-get install -y --no-install-recommends $APT_PACKAGES \
        && rm -rf /var/lib/apt/lists/*; \
    fi \
    && wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py38_4.8.3-Linux-x86_64.sh -O ~/miniconda.sh \
    && /bin/bash ~/miniconda.sh -b -p /opt/conda \
    && rm ~/miniconda.sh \
    && conda config --append channels conda-forge \
    && conda config --set auto_update_conda false \
    && conda config --set channel_priority strict \
    && if [ ! $PYTHON_VERSION = 3.8 ]; then \
           echo "installing Python=${PYTHON_VERSION}" \
           && conda install -Sy python=$PYTHON_VERSION; \
       fi \
    && conda update -S setuptools \
    && if [ ! -z $CONDA_PACKAGES ]; then \
           conda install -Sy $CONDA_PACKAGES \
           && conda clean --all -f -y; \
       fi \
    && if [ ! -z $PIP_VERSION ]; then \
           conda install -Sy pip=$PIP_VERSION \
           && conda clean --all -f -y; \
       fi \
    && if [ ! -z $PIP_PACKAGES ]; then \
           pip install --no-cache-dir $PIP_PACKAGES; \
       fi

# set working directory
WORKDIR $WORKDIR

# set default command
CMD ["python"]