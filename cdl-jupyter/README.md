# cdl-jupyter

A lightweight image ready to run a Jupyter notebook server, with only minimal IPython/Jupyter notebook-related packages 
installed.  To access the notebooks, `run` a container from the image and copy/paste the generated URL into a web browser.

#### Quick usage commands:
- Run a containerized notebook server using one of the pre-built images on Docker Hub directly:
```
docker run -v <path_to_notebooks>:/mnt -p 8888:8888 --name <container_name> contextlab/cdl-jupyter 
```
- Build from the GitHub repository to customize your own local version of the image (see `build-args`, below). Then, 
run your configured notebook server:
```
docker build https://github.com/ContextLab/cdl-docker-stacks.git#master:cdl-jupyter -t cdl-jupyter --build-arg <ARG>=<val> ...
docker run -v <path_to_notebooks>:/mnt -p 8888:8888 --name <container_name> cdl-jupyter
```


### `build-arg`s:
Arg | Default value | Description
----|-----|--------
`PYTHON_VERSION` | `3.8` | Python version for the container environment and notebooks. Must be one of the version tags available on Docker Hub. See below for addiional notes.
`APT_PACKAGES` | *empty* | Additional apt packages to install, if any. See below for a list of packages installed by default.
`CONDA_PACKAGES` | *empty* | Additional packages to install via the `conda` package manager, if any. See below for a list of packages installed by default.
`PIP_VERSION` | *empty* | Version of `pip` to install instead of the default version installed by `conda`.
`PIP_PACKAGES` | *empty* | Additional packages to install via `pip`, if any. See below for a list of packages installed by default.
`WORKDIR` | `/mnt` | Set the working directory inside the container **and** the root directory for the notebook server. Useful to specify if you want the notebook server to launch from a subdirectory of the host mount point, passed at runtime.
`NOTEBOOK_IP` | `0.0.0.0` | The IP address for the notebook server. May be overwritten if you want to run the notebook server remotely or publicly.
`PORT` | `8888` | The port exposed by the container and used to run the notebook server. Useful to override if you need to configure a firewall to allow access to the notebook server. If setting this, be sure to publish the correct port when running the container!

#### Additional notes:
- **Launch an interactive shell in the container**
   - By default, `run`ing or `start`ing the executing container will launch the notebook server.  If you instead want to 
   launch an interactive shell inside the container (e.g., to install a package or edit a config file), you can do so by:
      - _If you're running the container for the first time_, add `--entrypoint /bin/bash` to the end of your `run` command.    
      - _If you've previously run the container_, start it (`docker start <container_name>`) and run `docker exec -it <container_name> /bin/bash`
- **Specifying a Python version**
   - If you want to pass a Python version as a `--build-arg`, or it must correspond to one of the version tags available for 
   the `cdl-python` image on Docker Hub. If you want to build this image using an older version of Python or a specific 
   micro version, you can do so one of two ways:
      - Build the image with the default Python version, create a container, and launch an interactive shell (see above). 
      You can then install a version of Python (overwriting the default version) with `conda install python=<version>`. 
      Note that you may need to manually downgrade certain installed packages if you install a Python version older than 3.6.0.
      - Build the `cdl-python` image from GitHub (see "Quick usage commands", above), passing any Python version 
      (supported by `conda`) to the `PYTHON_VERSION` `build-arg`. Then, you can either A) run a from container and using 
      that image and manually install `notebook`, or B) [tag](https://docs.docker.com/engine/reference/commandline/tag/) 
      that image however you'd like and build the `cdl-jupyter` image, passing that same tag to the `PYTHON_VERSION` `build-arg`.
   
      Please note that while efforts have been made to enable the image to build in a version-agnostic way, only the 
      tagged versions on Docker Hub are officially supported, and using an older or newer Python version may lead to 
      unexpected behavior.
- **List of pre-installed packages for this image**:
   - `apt` packages:
   
      No additional packages installed for this image. See the [cdl-base image README](https://github.com/ContextLab/cdl-docker-stacks/tree/master/cdl-base/README.md) for a full list.
   - `conda` packages:
     
     Package | Version | use
     ----|----|-----------
     `notebook` | `6.1.3` | Main notebook application.
     `ipython` | *Python version-dependent*<sup>1</sup> | Interactive IPython shell application. Newest version compatible with the container's Python version is installed.
     `ipywidgets`<sup>2</sup> | `7.5.1` | JavaScript/IPython widget functionality for notebooks.
     `tqdm`<sup>2</sup> | `4.45.0` | Useful progress bar plugin for command line and notebooks.
     `nbconvert`<sup>2</sup> | `5.6.1` | Exports notebooks to various file formats
     `pandoc`<sup>2</sup> | `2.10` | Enables additional file formats for `nbconvert`
     `tini` | `0.18.0` | Handles signal forwarding and PID reaping to prevent notebook kernel crashes when running executable container
     
     <sup>1</sup>`python>=3.6`:`7.16.1`   `python>=3.5,<3.6`:`7.9.0`   `python>=3.3,<3.5`:`6.5.0`   `python<3.3`:`5.8.0`
     
     <sup>2</sup>Not installed for `python<3.6`
      
     _Note: dependencies installed by each package are not listed_