FROM contextlab/cdl-base

LABEL maintainer="Paxton Fitzpatrick <paxton.c.fitzpatrick@dartmouth.edu>"

# define other build-time variables
ARG APT_PACKAGES=""
ARG PYTHON_VERSION=3.8
ARG CONDA_PACKAGES=""
ARG PIP_VERSION=""
ARG PIP_PACKAGES=""
ARG WORKDIR="/mnt"

# Install miniconda, add conda-forge as a backup channel
# (combine with conditional install of apt packages to avoid caching intermediate)
RUN if [ ! -z $APT_PACKAGES ]; then { apt-get update --fix-missing eatmydata && \
                                      apt-get install -y $APT_PACKAGES && \
                                      rm -rf /var/lib/apt/lists/* }; fi && \
    echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py38_4.8.3-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh && \
    conda config --append channels conda-forge && \
    conda config --set auto_update_conda false && \
    conda config --set channel_priority strict && \
    conda config --set update_dependencies false
    if [ ! $PYTHON_VERSION = 3.8 ]; then { echo "installing Python=${PYTHON_VERSION}" && \
                                           conda install --yes python=$PYTHON_VERSION }; fi

# install Python packages
RUN conda update setuptools && \
    if [ ! -z $CONDA_PACKAGES ]; then conda install -y $CONDA_PACKAGES; fi && \
    if [ ! -z $PIP_VERSION ]; then conda install -y pip=$PIP_VERSION; fi && \
    if [ ! -z $PIP_PACKAGES ]; then pip install $PIP_PACKAGES; fi

# set working directory
WORKDIR $WORKDIR

# set default command
CMD ["python"]
