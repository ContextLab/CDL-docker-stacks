FROM contextlab/cdl-python:3.6

LABEL maintainer="Paxton Fitzpatrick <paxton.c.fitzpatrick@dartmouth.edu>"

# define build-time variables
ARG APT_PACKAGES=""
ARG CONDA_PACKAGES=""
ARG PIP_VERSION=""
ARG PIP_PACKAGES=""
ARG WORKDIR="/exp"
ARG MTURK=false

# we want the mountpoint to be the working directory, and psiturk to read from the .psiturkconfig there
ENV PSITURK_GLOBAL_CONFIG_LOCATION $WORKDIR
WORKDIR $WORKDIR

# PsiTurk containers can get pretty big, so combine steps to try to keep final image size down:
#   - install extra apt packages (if any)
#   - install extra conda packages (if any)
#   - install specific pip version (if passed)
#   - install PsiTurk (dependencies for v2.8.3 are pinned well, so we can skip installing them explicitly)
# done in this order so that pinned Psiturk dependency versions aren't overwritten
RUN apt-get update --fix-missing \
    && eatmydata apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        $APT_PACKAGES \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && conda update -S setuptools \
    && if [ ! -z $CONDA_PACKAGES ]; then \
           conda install -Sy $CONDA_PACKAGES \
           && conda clean --all -f -y; \
       fi \
    && if [ ! -z $PIP_VERSION ]; then \
           conda install -Sy pip=$PIP_VERSION \
           && conda clean --all -f -y; \
       fi \
    && pip install --no-cache-dir \
        $PIP_PACKAGES \
        psiturk==2.3.8 \
    && if [ $MTURK = true ]; then \
           pip install --no-cache-dir pymysql==0.10.0; \
       fi

# unset command from cdl-python
CMD []