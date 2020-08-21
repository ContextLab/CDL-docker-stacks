# cdl-python

simple image with (version-customizable) Python pre-installed via [Miniconda](https://docs.conda.io/en/latest/miniconda.html).  The image can be used in a number of useful ways:
- Quickly run a local Python script in a container, using the pre-built image on Docker Hub directly (`docker run -it --rm --name <your_container> -v "$PWD":/mnt contextlab/cdl-python python <your_script.py>`)
- Use the `Dockerfile` to build the image with custom options (see below), and run a local Python app inside a container environment (`docker run -it --rm --name <your_app_container> -v "$PWD":/mnt <built_image_name>`)
- Create a new image `FROM` the pre-built image on Docker Hub, `COPY` in your Python files, and run your app in a fully isolated environment (`docker run -it --rm --name <your_app> <child_image>`)


### `build-arg`s:
Arg | Default value | Description
----|-----|--------
`APT_PACKAGES` | *empty* | Additional apt packages to install, if any.
`MINICONDA_VERSION` | `4.8.3` | Miniconda installer version to use, from the [Miniconda installer archive](https://repo.anaconda.com/miniconda/). **Note**: must be a numbered version (i.e., not "latest") available for Linux x86_64.
`PYTHON_VERSION` | `3.8.5` | Python version to install.
`CONDA_PACKAGES` | *empty* | Packages to install via the `conda` package manager, if any.
`PIP_VERSION` | `20.2.2` | Version of `pip` to install instead of the default version installed by `conda`.
`PIP_PACKAGES` | *empty* | Packages to install via `pip`, if any.
`WORKDIR` | `/mnt` | Working directory inside the container.  Has no effect unless you're running a local Python script using the image directly.
