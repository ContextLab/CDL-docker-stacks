ARG PYTHON_VERSION=3.8
FROM contextlab/cdl-datasci:$PYTHON_VERSION

LABEL maintainer="Paxton Fitzpatrick <paxton.c.fitzpatrick@dartmouth.edu>"

# have to re-declare this here because FROM clears all args
ARG PYTHON_VERSION=3.8

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

# TODO: extra required apt packages for brainiak? seem to have auto-installed in Sherlock container
# TODO: once supereeg supports recent nilearn version and builds pass, should include here
RUN echo "Building with Python $PYTHON_VERSION" \
    && if [ -n "$APT_PACKAGES" ]; then \
           apt-get update --fix-missing \
           && eatmydata apt-get install -y --no-install-recommends $APT_PACKAGES \
           && rm -rf /var/lib/apt/lists/*; \
       fi \
    && conda install -Sy \
        datalad=0.13.3 \
        nibabel=3.1.1 \
        nilearn=0.6.2 \
        $CONDA_PACKAGES \
    && if [ -n "$PIP_VERSION" ]; then \
           conda install -Sy pip=$PIP_VERSION; \
       fi \
    && pip install --no-cache-dir \
        nltools==0.4.2 \
        $PIP_PACKAGES \
    && if [ "$PYTHON_VERSION" = 3.8 ]; then \
           pip install --no-cache-dir git+https://github.com/brainiak/brainiak.git@938151acff10cf49954f2c9933278de327b9da9d; \
       else \
           conda install -Sy -c brainiak brainiak=0.10; \
       fi \
    && conda clean --all -f -y \
