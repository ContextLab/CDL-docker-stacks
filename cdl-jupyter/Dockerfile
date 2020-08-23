ARG PYTHON_VERSION=3.8
FROM contextlab/cdl-python:$PYTHON_VERSION

LABEL maintainer="Paxton Fitzpatrick <paxton.c.fitzpatrick@dartmouth.edu>"

# define other build-time variables
ARG APT_PACKAGES=""
ARG CONDA_PACKAGES=""
ARG PIP_VERSION=""
ARG PIP_PACKAGES=""
ARG WORKDIR="/mnt"

ARG PORT=9999

# avoid unnecessarily caching intermediates, combine a bunch of conditional steps:
#   - install additional apt packages
#   - update Python version
#   - update pip
#   - install additional Python packages
# with definite steps:
#   - ensure setuptools is up to date
#   - install Tini for running container as executable
#   - install IPython, Jupyter notebook, and some other basic packages
#   - turn of Jedi autocomplete (evaluates code on TAB)
#   - install & enable some handy notebook extensions
RUN echo "Building with Python $PYTHON_VERSION" && \
    if [ ! -z $APT_PACKAGES ]; then { apt-get update --fix-missing eatmydata && \
                                      apt-get install -y $APT_PACKAGES && \
                                      rm -rf /var/lib/apt/lists/* }; fi && \
    conda update setuptools && \
    PY_MAJ_MIN="$(python -V | grep -Po '(?<=Python )([^.]*\.[^.]*)')" && \
        if (( $(echo "$PY_MAJ_MIN < 3.3" | bc -l) )); then IPYTHON_VERSION=5.8.0; \
        elif (( $(echo "$PY_MAJ_MIN < 3.5" | bc -l) )); then IPYTHON_VERSION=6.5.0; \
        elif (( $(echo "$PY_MAJ_MIN < 3.6" | bc -l) )); then IPYTHON_VERSION=7.9.0; \
        else IPYTHON_VERSION=7.16.1; fi && \
    conda install -y \
    tini=0.18.0 \
    notebook=6.1.3 \
    ipython=$IPYTHON_VERSION \
    $CONDA_PACKAGES && \
    if (( $(echo "$PY_MAJ_MIN >= 3.6" | bc -l) )); then { conda install \
        ipywidgets=7.5.1 \
        tqdm=4.45.0 \
        pandoc=2.10 \
        nbconvert=5.6.1 && \
        jupyter nbextension enable --py widgetsnbextension --sys-prefix }; fi && \
    if [ ! -z $PIP_VERSION ]; then conda install -y pip=$PIP_VERSION; fi && \
    pip install jupyter_contrib_nbextensions==0.5.1 $PIP_PACKAGES && \
    echo "c = get_config(); c.IPCompleter.use_jedi = False" > ~/.ipython/profile_default/ipython_config.py && \
    jupyter contrb nbextension install --sys-prefix


