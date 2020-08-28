ARG PYTHON_VERSION=3.8
FROM contextlab/cdl-jupyter:$PYTHON_VERSION

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

# again, reduce layers by combining a bunch of conditional steps:
#   - install additional apt packages
#   - install additional conda packages
#   - upgrade/downgrade pip
#   - install additional pip packages
# with definite steps:
#   - ensure setuptools is up to date
#   - install various common data science-related packages
RUN echo "Building with Python $PYTHON_VERSION" \
    && if [ ! -z $APT_PACKAGES ]; then \
           apt-get update --fix-missing \
           && eatmydata apt-get install -y --no-install-recommends $APT_PACKAGES \
           && rm -rf /var/lib/apt/lists/*; \
       fi \
    && conda update -S setupools \
    && conda install -Sy \
        beautifulsoup4=4.9.1 \
        bokeh=2.1.1 \
        h5py=2.10.0 \
        joblib=0.16.0 \
        matplotlib=3.2.2 \
        nltk=3.5 \
        numba=0.50.1 \
        numexpr=2.7.1 \
        numpy=1.18.5 \
        openpyxl=3.0.4 \
        pandas=1.0.5 \
        pandas-profiling=1.4.1 \
        plotly=4.8.2 \
        pymysql=0.9.3 \
        python-dateutil=2.8.1 \
        requests=2.24.0 \
        requests-ftp=0.3.1 \
        requests-kerberos=0.12.0 \
        scikit-image=0.16.2 \
        scikit-learn=0.23.1 \
        scipy=1.5.0 \
        seaborn=0.10.1 \
        sqlalchemy=1.3.18 \
        sqlalchemy-utils=0.36.5 \
        statsmodels=0.11.1 \
        sympy=1.6.1 \
        umap-learn=0.4.6 \
        urllib3=1.25.9 \
        word2vec=0.9.4 \
        xlrd=1.2.0 \
        $CONDA_PACKAGES \
    && if [ ! -z $PIP_VERSION ]; then \
           conda install -Sy pip=$PIP_VERSION; \
       fi \
    && conda clean --all -f -y \
    && pip install --no-cache-dir \
           git+https://github.com/ContextLab/hypertools.git@dea0df127b150c39ed9a7b1faaa8fbde089ee834 \
           quail==0.2.0 \
           $PIP_PACKAGES