import time
from os import getenv


CDL_JUPYTER_APT_PACKAGES = ['bc', 'bzip2']


def start_notebook_server(container, wait_time=10):
    """helper function for running notebook server"""
    notebook_server = container.run(command=None, shell=None, max_wait=-1)
    time.sleep(wait_time)
    notebook_server.stop()
    return notebook_server


########################################
#            CONTAINER TESTS           #
########################################
def test_jupyter_apt_packages_installed(container):
    for apt_pkg in CDL_JUPYTER_APT_PACKAGES:
        pkg_installed = container.apt_packages.get(apt_pkg)
        assert pkg_installed is not None, f'{apt_pkg} is not installed'
        assert pkg_installed == 'manual', (f'{apt_pkg} was installed as a '
                                           'dependency of another package, '
                                           'not manually')


def test_ipython_config_in_container(container):
    output = container.run('ls ~/.ipython/profile_default').logs()
    assert 'ipython_config.py' in output.decode('utf-8').strip().split()


def test_jedi_completion_disabled(container):
    configured_options = container.run(
        "grep '^[^#]' ~/.ipython/profile_default/ipython_config.py",
        detach=False,
        remove=True
    ).splitlines()
    assert 'c.Completer.use_jedi = False' in configured_options
    if float(getenv("PYTHON_VERSION")) > 3.6:
        # option not present in IPython version installed for Python 3.6 images
        assert 'c.IPCompleter.use_jedi = False' in configured_options


def test_nbextensions_enabled(container):
    extensions = [
        'jupyter-js-widgets/extension',
        'nbextensions_configurator/config_menu/main',
        'contrib_nbextensions_help_item/main',
        'nbextensions_configurator/tree_tab/main'
    ]
    output = container.run('jupyter nbextension list',
                           detach=False,
                           remove=True,
                           tty=False)
    # remove ANSI color codes (still there despite tty=False)
    output = output.replace('\x1b[32m', '').replace('\x1b[31m', '').replace('\x1b[0m', '')
    for line in output.splitlines():
        line = line.strip()
        for ext in extensions:
            if line.startswith(ext):
                assert line.endswith('enabled'), f'{ext} is not enabled'
                extensions.remove(ext)
                break

    assert len(extensions) == 0, f"notebook extensions not configured:\n\t{', '.join(extensions)}"


########################################
#         NOTEBOOK SERVER TESTS        #
########################################
def test_nbextensions_configurator_enabled(container, conda_env):
    notebook_server = start_notebook_server(container)
    configurator_version = conda_env.installed_packages.get(
        'jupyter_nbextensions_configurator'
    ).version
    nb_server_logs = notebook_server.logs().decode('utf-8').strip().splitlines()
    expected_log_msg = f'[jupyter_nbextensions_configurator] enabled {configurator_version}'
    assert nb_server_logs[1].endswith(expected_log_msg)


def test_server_runs_from_workdir(container):
    notebook_server = start_notebook_server(container)
    expected_workdir = container.expected_attrs.get('workdir')
    # if container.custom_build:
    #     # pop the value if it's a custom-built container in order to
    #     # prep for `test_all_custom_build_args_tested()`
    #     container.expected_attrs.pop('workdir')

    nb_server_logs = notebook_server.logs().decode('utf-8').strip().splitlines()
    expected_log_msg = f'Serving notebooks from local directory: {expected_workdir}'
    assert nb_server_logs[2].endswith(expected_log_msg)


def test_server_provides_login_token(container):
    notebook_server = start_notebook_server(container)
    notebook_server_logs = notebook_server.logs().decode('utf-8').strip()
    assert '/?token=' in notebook_server_logs


def test_notebook_server_port(container):
    expected_port = container.expected_attrs.get('port')
    # if container.custom_build:
    #     container.expected_attrs.pop('port')

    notebook_server = start_notebook_server(container)
    notebook_server_logs = notebook_server.logs().decode('utf-8').strip()
    assert f':{expected_port}/' in notebook_server_logs


# TODO: import requests; requests.get(notebook_url) -- how to confirm token is valid?)
