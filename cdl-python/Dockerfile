FROM contextlab/cdl-base

LABEL maintainer="Paxton Fitzpatrick <paxton.c.fitzpatrick@dartmouth.edu>"

# define build-time variables
ARG APT_PACKAGES=""
ARG PYTHON_VERSION=3.8
ARG CONDA_PACKAGES=""
ARG PIP_VERSION=""
ARG PIP_PACKAGES=""
ARG WORKDIR="/mnt"

# Install miniconda & any additional apt packages
RUN if [ ! -z $APT_PACKAGES ]; then { apt-get update --fix-missing eatmydata && \
                                      apt-get install -y --no-install-recommends $APT_PACKAGES && \
                                      rm -rf /var/lib/apt/lists/* }; fi && \
    echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py38_4.8.3-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh

# setup conda config, (optionally) install specific Python version, (optionally) install Python packages
RUN conda config --append channels conda-forge && \
    conda config --set auto_update_conda false && \
    conda config --set channel_priority strict && \
    conda config --set update_dependencies false
    if [ ! $PYTHON_VERSION = 3.8 ]; then { echo "installing Python=${PYTHON_VERSION}" && \
                                           conda install -y python=$PYTHON_VERSION }; fi && \
    conda update setuptools && \
    if [ ! -z $CONDA_PACKAGES ]; then { conda install -y $CONDA_PACKAGES && conda clean --all -f -y }; fi && \
    if [ ! -z $PIP_VERSION ]; then { conda install -y pip=$PIP_VERSION && conda clean --all -f -y }; fi && \
    if [ ! -z $PIP_PACKAGES ]; then pip install --no-cache-dir $PIP_PACKAGES; fi

# set working directory
WORKDIR $WORKDIR

# set default command
CMD ["python"]
