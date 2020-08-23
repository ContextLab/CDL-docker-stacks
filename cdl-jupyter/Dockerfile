ARG PYTHON_VERSION=3.8
FROM contextlab/cdl-python:$PYTHON_VERSION

LABEL maintainer="Paxton Fitzpatrick <paxton.c.fitzpatrick@dartmouth.edu>"

# define other build-time variables
ARG APT_PACKAGES=""
ARG CONDA_PACKAGES=""
ARG PIP_VERSION=""
ARG PIP_PACKAGES=""
ARG WORKDIR="/mnt"
ARG NOTEBOOK_IP=0.0.0.0
ARG PORT=8888

# set build args read by jupyter_notebook_config.py to environment variables
ENV NOTEBOOK_DIR $WORKDIR
ENV NOTEBOOK_IP $NOTEBOOK_IP
ENV NOTEBOOK_PORT $PORT

# reduce layers by combining a bunch of conditional steps:
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
    apt-get update --fix-missing &&
    eatmydata apt-get install -y --no-install-recommends \
        bc \
        bzip2 \
    if [ ! -z $APT_PACKAGES ]; then { apt-get update --fix-missing eatmydata && \
                                      apt-get install -y --no-install-recommends $APT_PACKAGES && \
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
        jupyter nbextension enable --py widgetsnbextension --user }; fi && \
    if [ ! -z $PIP_VERSION ]; then conda install -y pip=$PIP_VERSION; fi && \
    conda clean --all -f -y && \
    pip install --no-cache-dir jupyter_contrib_nbextensions==0.5.1 $PIP_PACKAGES && \
    jupyter notebook --generate-config && \
    jupyter contrb nbextension install --user && \
    echo "c = get_config(); c.IPCompleter.use_jedi = False" > ~/.ipython/profile_default/ipython_config.py

# set working directory
WORKDIR $WORKDIR

# set entrypoint & command to run container as executable
# (can be overridden for interactive session via args to docker run or docker exec)
ENTRYPOINT ["tini", "-g", "--"]
CMD ["jupyter", "notebook"]

# expose port for notebook server
EXPOSE $PORT

# copy in files as late as possible
COPY jupyter_notebook_config.py $HOME/.jupyter/