ARG PYTHON_VERSION=3.8
FROM contextlab/cdl-datasci:$PYTHON_VERSION

LABEL maintainer="Paxton Fitzpatrick <paxton.c.fitzpatrick@dartmouth.edu>"

# define other build-time variables
ARG APT_PACKAGES=""
ARG CONDA_PACKAGES=""
ARG PIP_VERSION=""
ARG PIP_PACKAGES=""
ARG WORKDIR="/mnt"
ARG NOTEBOOK_IP=0.0.0.0
ARG PORT=8888

# update relevant environment variables set in base image in case they were passed here
ENV NOTEBOOK_DIR $WORKDIR
ENV NOTEBOOK_IP $NOTEBOOK_IP
ENV NOTEBOOK_PORT $PORT

# also update working directory, in case passed here
WORKDIR $WORKDIR

# reduce layers by combining a bunch of conditional steps:
#   - install additional apt packages
#   - install additional conda packages
#   - upgrade/downgrade pip
#   - install additional pip packages
# with definite steps:
#   - ensure setuptools is up to date
#   - install gcc for brainiak
#   - install various common neuroscience-related packages
# TODO: extra required apt packages for brainiak? seem to have auto-installed in Sherlock container
# TODO: once supereeg supports recent nilearn version and builds pass, should include here
RUN echo "Building with Python $PYTHON_VERSION" \
    && if [ ! -z $APT_PACKAGES ]; then \
           apt-get update --fix-missing \
           && eatmydata apt-get install -y --no-install-recommends $APT_PACKAGES \
           && rm -rf /var/lib/apt/lists/*; \
       fi \
    && conda update -S setupools \
    && conda install -Sy \
        gcc \
        datalad=0.13.3 \
        nibabel=3.1.1 \
        nilearn=0.6.2 \
        brainiak=0.7.1 \
        $CONDA_PACKAGES
    && if [ ! -z $PIP_VERSION ]; then \
           conda install -Sy pip=$PIP_VERSION; \
       fi \
    && conda clean --all -f -y \
    && pip install --no-cache-dir \
        nltools==0.4.1 \
        $PIP_PACKAGES