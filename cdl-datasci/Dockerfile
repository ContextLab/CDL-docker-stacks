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
#   - upgrade/downgrade pip
#   - install additional Python packages
# with definite steps:
#   - ensure setuptools is up to date
#   - install various common data science-related packages
RUN conda update -S setupools \
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
        seaborn=0.10.1 \




