import os
import tarfile

import pytest


########################################
#            CONTAINER TESTS           #
########################################
def test_correct_python_version_installed(container, conda_env):
    expected_version = container.expected_attrs.get('python_version')
    installed_version = conda_env.installed_packages.get('python')
    assert installed_version.matches_version(expected_version)


def test_correct_workdir_set(container):
    expected_workdir = container.expected_attrs.get('workdir')
    if container.custom_build:
        # pop the value if it's a custom-built container in order to
        # prep for `test_all_custom_build_args_tested()`
        container.expected_attrs.pop('workdir')

    actual_workdir = container.run('pwd', detach=False, remove=True)
    assert actual_workdir == expected_workdir


def test_pin_package_script_in_profile(container):
    output = container.run('ls --almost-all /etc/profile.d', detach=False, remove=True)
    assert 'pin_conda_package_version.sh' in output


def test_pip_cache_removed(container):
    c = container.run('ls -a ~/.cache/pip', remove=False)
    log = c.logs().decode('utf-8').strip()
    assert 'No such file or directory' in log


@pytest.mark.no_inherit_test
def test_python_default_cmd(container):
    c = container.run(command=None, shell=None, max_wait=-1)
    c.stop(timeout=1)
    default_cmd = c.attrs.get('Config').get('Cmd')
    assert default_cmd == ['python']


def test_run_script_mounted(container):
    repo_root = os.getenv("GITHUB_WORKSPACE")
    mountpoint_local = os.path.join(repo_root, 'cdl-python', 'ci')
    script_path = os.path.join(mountpoint_local, 'simple_script.py')
    expected_testfile_path = os.path.join(mountpoint_local, 'testfile.txt')
    c = container.run(['simple_script.py', 'testfile.txt'],
                      shell='python',
                      shell_flags=None,
                      mountpoint_container='/mnt',
                      mountpoint_local=mountpoint_local)
    lines = c.logs().decode('utf-8').strip().splitlines()

    # two print statements should've been executed
    assert len(lines) == 2, lines

    # text should be the same before/after being written to/read from file
    orig_message, file_message = lines
    assert orig_message == file_message, \
        f'ORIGINAL:\n{orig_message}\n\nFILE:\n{file_message}'

    # should be able to access hostname from inside container, and it
    # should match the container ID (first 12 characters)
    hostname = orig_message.replace("Hello, world! I'm ", '').split()[0]
    container_id = c.id[:len(hostname)]
    assert hostname == container_id, \
        f'HOSTNAME:\t{hostname}\nCONTAINER ID\t{container_id}'

    # should be able to read the Python version from inside the container
    inside_py_version = orig_message.split()[-1]
    outside_py_version = container.expected_attrs.get('python_version')
    assert inside_py_version == outside_py_version

    # file should exist at expected location
    assert os.path.isfile(expected_testfile_path)

    # clean up
    os.remove(expected_testfile_path)


def test_run_script_unmounted(container):
    # store cwd to return to after test
    cwd = os.getcwd()
    repo_root = os.getenv("GITHUB_WORKSPACE")
    ci_dir = os.path.join(repo_root, 'cdl-python', 'ci')
    script_name = 'simple_script.py'
    tarfile_name = f'{script_name}.tar'
    dest_filepath = f'/mnt/{script_name}'

    # run from dir of tarfile so container paths are created correctly
    os.chdir(ci_dir)
    with tarfile.open(tarfile_name, 'w') as tf:
        tf.add(script_name)

    # start background process to keep container running
    c = container.run('sleep infinity', max_wait=-1)
    with open(tarfile_name, 'rb') as tf:
        # Python API method of implementing docker cp
        c.put_archive('/mnt', tf)

    exit_code, output = c.exec_run(['python', dest_filepath, 'testfile.txt'],
                                   detach=False,
                                   tty=True,
                                   stdout=True,
                                   stderr=True,
                                   demux=True)
    stdout, stderr = output
    if stdout is not None:
        stdout = stdout.decode('utf-8').strip()
    if stderr is not None:
        stderr = stderr.decode('utf-8').strip()

    assert exit_code == 0, f'command failed with exit code: {exit_code}.\nstderr:\n{stderr}'

    lines = stdout.splitlines()

    # two print statements should've been executed
    assert len(lines) == 2, lines

    # text should be the same before/after being written to/read from file
    orig_message, file_message = lines
    assert orig_message == file_message, \
        f'ORIGINAL:\n{orig_message}\n\nFILE:\n{file_message}'

    # should be able to access hostname from inside container, and it
    # should match the container ID (first 12 characters)
    hostname = orig_message.replace("Hello, world! I'm ", '').split()[0]
    container_id = c.id[:len(hostname)]
    assert hostname == container_id, \
        f'HOSTNAME:\t{hostname}\nCONTAINER ID\t{container_id}'

    # should be able to read the Python version from inside the container
    inside_py_version = orig_message.split()[-1]
    outside_py_version = container.expected_attrs.get('python_version')
    assert inside_py_version == outside_py_version

    # file should exist at expected location
    exit_code, output = c.exec_run(['/bin/bash', '-c', f'stat {dest_filepath}'],
                                   detach=False,
                                   tty=True,
                                   stdout=True,
                                   stderr=True,
                                   demux=True)
    stdout, stderr = output
    if stdout is not None:
        stdout = stdout.decode('utf-8').strip()
    if stderr is not None:
        stderr = stderr.decode('utf-8').strip()

    assert exit_code == 0, f'command failed with exit code: {exit_code}.\nstderr:\n{stderr}'
    assert "No such file or directory" not in stdout

    # clean up
    os.remove(tarfile_name)
    os.chdir(cwd)
    c.stop()


########################################
#        CONDA ENVIRONMENT TESTS       #
########################################
def test_conda_bin_in_path(container, conda_env):
    path = container.run('echo $PATH', detach=False, remove=True, tty=False)
    conda_bin = f"{conda_env.config.get('root_prefix')}/bin"
    assert path.startswith(conda_bin)


def test_no_auto_update_conda(conda_env):
    auto_update = conda_env.config.get('auto_update_conda')
    assert auto_update is False


def test_no_notify_outdated_conda(conda_env):
    notify_outdated = conda_env.config.get('notify_outdated_conda')
    assert notify_outdated is False


def test_channel_order(conda_env):
    channels = conda_env.config.get('channels')
    assert channels == ['conda-forge', 'defaults']


def test_strict_channel_priority(conda_env):
    priority = conda_env.config.get('channel_priority')
    assert priority == 'strict'


def test_conda_cache_cleaned(container, conda_env):
    pkgs_dirs = conda_env.config.get('pkgs_dirs')
    for pkg_dir in pkgs_dirs:
        c = container.run(f'ls -a {pkg_dir}', detach=True, remove=False)
        log = c.logs().decode('utf-8').strip()
        assert 'No such file or directory' in log
        c.remove()


# TODO: figure out how to parametrize this with pytest-cases rather than looping
def test_pinned_versions_installed(conda_env):
    for pkg_name, pinned_pkg in conda_env.pinned_packages.items():
        installed_pkg = conda_env.installed_packages.get(pkg_name)
        assert installed_pkg is not None, \
            f'pinned package {pinned_pkg} is not installed'
        assert installed_pkg.matches_version(pinned_pkg), \
            f'installed version of {pkg_name} ({installed_pkg}) does not match ' \
            f'pinned version ({pinned_pkg}'


# TODO: figure out how to parametrize this with pytest-cases rather than looping
def test_requested_versions_installed(conda_env):
    for pkg_name, requested_pkg in conda_env.requested_packages.items():
        installed_pkg = conda_env.installed_packages.get(pkg_name)
        assert installed_pkg is not None, \
            f'requested package {requested_pkg} is not installed'
        assert installed_pkg.matches_version(requested_pkg), \
            f'installed version of {pkg_name} ({installed_pkg}) does not match ' \
            f'requested version ({requested_pkg})'


# TODO: add test to import each module to check if installed properly and working


########################################
#        CUSTOM BUILD-ARG TESTS        #
########################################
@pytest.mark.custom_build_test
def test_custom_apt_packages_installed(container):
    custom_apt_pkgs = container.expected_attrs.pop('apt_packages')
    for apt_pkg in custom_apt_pkgs:
        pkg_installed = container.apt_packages.get(apt_pkg)
        assert pkg_installed is not None, \
            f'custom apt package {apt_pkg} is not installed'
        assert pkg_installed == 'manual', \
            f'custom apt package {apt_pkg} was installed as a dependency of ' \
            'another package, not manually'


@pytest.mark.custom_build_test
def test_custom_conda_packages_installed(container, conda_env):
    custom_conda_pkgs = container.expected_attrs.pop('conda_packages')
    if isinstance(custom_conda_pkgs, str):
        custom_conda_pkgs = [custom_conda_pkgs]

    for pkg_spec in custom_conda_pkgs:
        # needs to handle both forms: pkg & pkg=version
        pkg_name = pkg_spec.split('=')[0]
        installed_pkg = conda_env.installed_packages.get(pkg_name)
        assert installed_pkg is not None, \
            f'conda package {pkg_spec} from build-arg not installed'
        if '=' in pkg_spec:
            pkg_version = pkg_spec.split('=')[1]
            assert installed_pkg.matches_version(pkg_version), \
                f'conda-installed version of package {pkg_name}, ' \
                f'{installed_pkg.version} does not match build-arg specified ' \
                f'version, {pkg_version}'


@pytest.mark.custom_build_test
def test_custom_pip_version_installed(container, conda_env):
    custom_pip_version = container.expected_attrs.pop('pip_version')
    installed_pip_version = conda_env.installed_packages.get('pip')
    assert installed_pip_version.matches_version(custom_pip_version)


@pytest.mark.custom_build_test
def test_custom_pip_packages_installed(container, conda_env):
    custom_pip_pkgs = container.expected_attrs.pop('pip_packages')
    if isinstance(custom_pip_pkgs, str):
        custom_pip_pkgs = [custom_pip_pkgs]
    # needs to handle both forms: pkg & pkg==version
    for pkg_spec in custom_pip_pkgs:
        if 'git' in pkg_spec:
            pkg_name = pkg_spec.split('.git')[0].split('/')[-1]
        else:
            pkg_name = pkg_spec.split('=')[0]

        installed_pkg = conda_env.installed_packages.get(pkg_name)
        assert installed_pkg is not None, \
            f'pip package {pkg_spec} from build-arg not installed'
        # `conda env export` command shows most recent tag for git-based
        # packages, so can't test that if installed from a commit hash
        if '=' in pkg_spec:
            pkg_version = pkg_spec.split('=')[1]
            assert installed_pkg.matches_version(pkg_version), \
                f'pip-installed version of package {pkg_name}, ' \
                f'{installed_pkg.version} does not match build-arg specified ' \
                f'version, {pkg_version}'


@pytest.mark.custom_build_test
@pytest.mark.last
def test_all_custom_build_args_tested(container):
    # each custom_build_tests pops the attr tested, so if all have been
    # covered by tests, none should be left by the last test (except
    # python_version, which isn't changed for custom builds)
    untested_attrs = container.expected_attrs
    try:
        untested_attrs.pop('python_version')
    except KeyError:
        pass

    assert len(untested_attrs) == 0
