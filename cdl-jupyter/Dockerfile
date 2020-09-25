ARG PYTHON_VERSION=3.8
FROM contextlab/cdl-python:$PYTHON_VERSION

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

# set build args read by jupyter_notebook_config.py to environment variables
ENV NOTEBOOK_DIR $WORKDIR
ENV NOTEBOOK_IP $NOTEBOOK_IP
ENV NOTEBOOK_PORT $PORT

# reduce layers by combining a bunch of conditional steps:
#   - install additional apt packages
#   - upgrade/downgrade pip
#   - install additional Python packages
# with definite steps:
#   - install Tini for running container as executable
#   - install IPython, Jupyter notebook, and some other basic packages
#   - turn off Jedi autocomplete (evaluates code on TAB)
#   - install & enable some handy notebook extensions
RUN echo "Building with Python $PYTHON_VERSION" \
    && apt-get update --fix-missing \
    && eatmydata apt-get install -y --no-install-recommends \
        bc \
        bzip2 \
        $APT_PACKAGES \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && PY_MAJ_MIN="$(python -V | grep -Po '(?<=Python )([^.]*\.[^.]*)')" \
    && if (( $(echo "$PY_MAJ_MIN < 3.3" | bc -l) )); then \
           IPYTHON_VERSION=5.8.0; \
       elif (( $(echo "$PY_MAJ_MIN < 3.5" | bc -l) )); then \
           IPYTHON_VERSION=6.5.0; \
       elif (( $(echo "$PY_MAJ_MIN < 3.6" | bc -l) )); then \
           IPYTHON_VERSION=7.9.0; \
       else \
           IPYTHON_VERSION=7.16.1; \
       fi \
    && conda install -Sy \
        tini=0.18.0 \
        notebook=6.1.4 \
        ipython=$IPYTHON_VERSION \
        $CONDA_PACKAGES \
    && source /etc/profile.d/pin_conda_package_version.sh \
    && pin_package tini exact \
    && pin_package jupyter minor min \
    && pin_package notebook minor min \
    && pin_package ipython exact \
    && if (( $(echo "$PY_MAJ_MIN >= 3.6" | bc -l) )); then \
           conda install -Sy \
               ipywidgets=7.5.1 \
               jupyter_contrib_nbextensions=0.5.1 \
               nbconvert=5.6.1 \
               pandoc=2.10 \
           && pin_package jupyter_contrib exact \
           && pin_package nbconvert minor min \
           && jupyter nbextension enable --py widgetsnbextension --sys-prefix; \
       fi \
    && if [ -n "$PIP_VERSION" ]; then \
           conda install -Sy pip=$PIP_VERSION \
           && pin_package pip major; \
       fi \
    && conda clean --all -f -y \
    && if [ -n "$PIP_PACKAGES" ]; then \
           pip install $PIP_PACKAGES \
           && rm -rf ~/.cache/pip; \
       fi \
    && jupyter notebook --generate-config \
    && ipython profile create \
    &&  sed -i \
        -e 's/^# c.Completer.use_jedi = True/c.Completer.use_jedi = False/' \
        -e 's/^#c.Completer.use_jedi = True/c.Completer.use_jedi = False/' \
        -e 's/^# c.IPCompleter.use_jedi = True/c.IPCompleter.use_jedi = False/' \
        ~/.ipython/profile_default/ipython_config.py

# set working directory
WORKDIR $WORKDIR

# set entrypoint & command to run container as executable
# (can be overridden for interactive session via args to docker run or docker exec)
ENTRYPOINT ["tini", "-g", "--"]
CMD ["jupyter", "notebook"]

# copy in files as late as possible
COPY jupyter_notebook_config.py /root/.jupyter/