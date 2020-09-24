FROM contextlab/cdl-base:latest

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

COPY pin_conda_package_version.sh /etc/profile.d/

# Install miniconda & any additional apt packages
RUN if [ -n "$APT_PACKAGES" ]; then \
        apt-get update --fix-missing \
        && eatmydata apt-get install -y --no-install-recommends $APT_PACKAGES \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*; \
    fi \
    && wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-py38_4.8.3-Linux-x86_64.sh -O ~/miniconda.sh \
    && /bin/bash ~/miniconda.sh -b -p /opt/conda \
    && rm ~/miniconda.sh \
    && conda config --set auto_update_conda false \
    && conda config --set notify_outdated_conda false \
    && conda config --prepend channels conda-forge \
    && conda config --set channel_priority strict \
    && conda config --set show_channel_urls true \
    && conda config --set remote_max_retries 5 \
    && if [ ! "$PYTHON_VERSION" = 3.8 ]; then \
           echo "installing Python=${PYTHON_VERSION}" \
           && conda install -y python=$PYTHON_VERSION; \
       fi \
    && conda install -Sy \
           conda=4.8.4 \
           setuptools=49.6.0 \
           pip=20.0.2 \
    && if [ -n "$CONDA_PACKAGES" ]; then \
           conda install -y $CONDA_PACKAGES \
           && conda clean --all -f -y; \
       fi \
    && if [ -n "$PIP_VERSION" ]; then \
           conda install -Sy pip=$PIP_VERSION; \
       fi \
    && if [ -n "$PIP_PACKAGES" ]; then \
           pip install $PIP_PACKAGES \
           && rm -rf ~/.cache/pip; \
       fi \
    && conda clean --all -f -y \
    && source /etc/profile.d/pin_conda_package_version.sh \
    && pin_package python minor equal \
    && pin_package conda minor equal \
    && pin_package setuptools major min \
    && pin_package pip major min

# set working directory
WORKDIR $WORKDIR

# set default command
CMD ["python"]