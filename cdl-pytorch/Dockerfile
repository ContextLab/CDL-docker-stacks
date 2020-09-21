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

# set pytorch-specifc environment variable
ENV NO_CUDA 1

# also update working directory, in case passed here
WORKDIR $WORKDIR

RUN echo "Building with Python $PYTHON_VERSION" \
    && if [ -n "$APT_PACKAGES" ]; then \
           apt-get update --fix-missing \
           && eatmydata apt-get install -y --no-install-recommends $APT_PACKAGES \
           && apt-get clean \
           && rm -rf /var/lib/apt/lists/*; \
       fi \
    && (conda install -Sy -c pytorch \
        pytorch=1.6 \
        torchvision=0.7 \
        cpuonly \
        $CONDA_PACKAGES \
    || pip install --no-cache-dir \
        torch==1.6.0+cpu \
        torchvision==0.7.0+cpu \
        -f https://download.pytorch.org/whl/torch_stable.html) \
    && source /etc/profile.d/pin_conda_package_version.sh \
    && pin_package pytorch exact equal \
    && pin_package torchvision exact equal \
    && pin_package cpuonly exact equal \
    && if [ -n "$PIP_VERSION" ]; then \
           conda install -Sy pip=$PIP_VERSION \
           && pin_package pip major min; \
       fi \
    && conda clean --all -f -y \
    && if [ -n "$PIP_PACKAGES" ]; then \
           pip install --no-cache-dir $PIP_PACKAGES; \
       fi