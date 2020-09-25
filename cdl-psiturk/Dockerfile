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
RUN if [ -n "$APT_PACKAGES" ]; then \
        apt-get update --fix-missing \
        && eatmydata apt-get install -y --no-install-recommends $APT_PACKAGES \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*; \
    fi \
    && conda install -Sy \
        ciso8601=2.1.3 \
        git=2.28.0 \
        psutil=5.6.7 \
        requests-oauthlib=1.3.0 \
        setproctitle=1.1.10 \
        $CONDA_PACKAGES \
    && if [ -n "$PIP_VERSION" ]; then \
           conda install -Sy pip=$PIP_VERSION; \
       fi \
    && conda clean --all -f -y \
    && pip install \
        psiturk==2.3.8 \
        $PIP_PACKAGES \
    && if [ $MTURK = true ]; then \
           pip install pymysql==0.10.0; \
       fi \
    && rm -rf ~/.cache/pip

# set PsiTurk shell to launch automatically when run
CMD ["psiturk"]