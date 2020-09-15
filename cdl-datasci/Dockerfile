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
    && apt-get update --fix-missing \
    && eatmydata apt-get install -y --no-install-recommends \
        git \
        $APT_PACKAGES \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && conda install -Sy \
        beautifulsoup4=4.9.1 \
        bokeh=2.1.1 \
        h5py=2.10.0 \
        joblib=0.16.0 \
        matplotlib=3.2.2 \
        nltk=3.4.4 \
        numba=0.50.1 \
        numexpr=2.7.1 \
        numpy=1.19.1 \
        openpyxl=3.0.5 \
        pandas=1.1.2 \
        pandas-profiling=2.9.0 \
        plotly=4.10.0 \
        pymysql=0.10.1 \
        pynndescent=0.4.8 \
        scikit-image=0.17.2 \
        scikit-learn=0.23.2 \
        scipy=1.5.2 \
        seaborn=0.11.0 \
        sqlalchemy=1.3.19 \
        sqlalchemy-utils=0.36.6 \
        statsmodels=0.12.0 \
        sympy=1.6.2 \
        umap-learn=0.4.6 \
        word2vec=0.9.4 \
        xlrd=1.2.0 \
        $CONDA_PACKAGES \
    && source /etc/profile.d/pin_conda_package_version.sh \
    && pin_package bokeh minor min \
    && pin_package matplotlib minor min \
    && pin_package nltk minor min \
    && pin_package numba minor min \
    && pin_package numpy exact min \
    && pin_package pandas minor \
    && pin_package plotly minor min \
    && pin_package scikit-learn minor min \
    && pin_package scipy exact min \
    && pin_package seaborn exact min \
    && pin_package umap-learn exact min \
    && if [ -n "$PIP_VERSION" ]; then \
           conda install -Sy pip=$PIP_VERSION; \
       fi \
    && conda clean --all -f -y \
    && pip install --no-cache-dir \
           git+https://github.com/paxtonfitzpatrick/hypertools.git@11aa6e84607e936179727dc4ecbcbac16c68cc98 \
           quail==0.2.0 \
           fastdtw==0.3.4 \
           $PIP_PACKAGES \
