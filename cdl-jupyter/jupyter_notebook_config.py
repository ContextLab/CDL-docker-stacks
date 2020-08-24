# Config file with some read by the notebook server, with some options
# that make running notebooks inside a container easier

import os

ip = os.environ.get("NOTEBOOK_IP")
port = os.environ.get("NOTEBOOK_PORT")
notebook_dir = os.environ.get("NOTEBOOK_DIR")

c = get_config()
c.NotebookApp.ip = ip
c.NotebookApp.port = port
c.NotebookApp.notebook_dirUnicode = notebook_dir
c.NotebookApp.open_browser = False
c.NotebookApp.allow_rootBool = True
# https://github.com/jupyter/notebook/issues/3130
c.FileContentsManager.delete_to_trash = False
