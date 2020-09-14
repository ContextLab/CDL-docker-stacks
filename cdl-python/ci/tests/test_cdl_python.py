import pytest


CDL_BASE_APT_PACKAGES = [
    'eatmydata'
    'ca-certificates',
    'mpich',
    'procps',
    'sudo',
    'vim',
    'wget'
]


########################################
#            CONTAINER TESTS           #
########################################
# TODO: dynamically add apt packages from other parent Dockerfiles
def test_apt_packages_installed(container):
    for apt_pkg in CDL_BASE_APT_PACKAGES:
        pkg_installed = container.apt_packages.get(apt_pkg)
        assert pkg_installed is not None, f'{apt_pkg} is not installed'
        assert (pkg_installed == 'manual',
                f'{apt_pkg} was installed as a dependency of another package, '
                'not manually')


def test_correct_python_version_installed(container, conda_env):
    expected_version = container.expected_attrs.get('PYTHON_VERSION')
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


@pytest.mark.no_inherit_test
def test_python_default_cmd(container):
    c = container.run(shell=None)
    c.stop(timeout=1)
    c.remove()
    default_cmd = c.attrs.get('Config').get('Cmd')
    assert default_cmd == ['python']


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
        c = container.run(f'ls {pkg_dir}', remove=False)
        log = c.logs().decode('utf-8').strip()
        assert 'No such file or directory' in log
        c.remove()




# TODO: figure out how to parametrize this with pytest-cases rather than looping
def test_pinned_versions_installed(conda_env):
    for pkg_name, pinned_pkg in conda_env.pinned_packages.items():
        installed_pkg = conda_env.installed_packages.get(pkg_name)
        assert (installed_pkg is not None,
                f'pinned package {pinned_pkg} is not installed')
        assert (installed_pkg.matches_version(pinned_pkg),
                f'installed version of {pkg_name} ({installed_pkg}) does not '
                f'match pinned version ({pinned_pkg}')


# TODO: figure out how to parametrize this with pytest-cases rather than looping
def test_requested_versions_installed(conda_env):
    for pkg_name, requested_pkg in conda_env.requested_packages.items():
        installed_pkg = conda_env.installed_packages.get(pkg_name)
        assert (installed_pkg is not None,
                f'requested package {requested_pkg} is not installed')
        assert (installed_pkg.matches_version(requested_pkg),
                f'installed version of {pkg_name} ({installed_pkg}) does not '
                f'match requested version ({requested_pkg}')


########################################
#        CUSTOM BUILD-ARG TESTS        #
########################################
@pytest.mark.custom_build_test
def test_custom_apt_packages_installed(container):
    custom_apt_pkgs = container.expected_attrs.pop('apt_packages')
    for apt_pkg in custom_apt_pkgs:
        pkg_installed = container.apt_packages.get(apt_pkg)
        assert (pkg_installed is not None,
                f'custom apt package {apt_pkg} is not installed')
        assert (pkg_installed == 'manual',
                f'custom apt package {apt_pkg} was installed as a dependency '
                'of another package, not manually')


@pytest.mark.custom_build_test
def test_custom_conda_packages_installed(container, conda_env):
    custom_conda_pkgs = container.expected_attrs.pop('conda_packages')
    if isinstance(custom_conda_pkgs, str):
        custom_conda_pkgs = [custom_conda_pkgs]

    for pkg_spec in custom_conda_pkgs:
        # needs to handle both forms: pkg & pkg=version
        pkg_name = pkg_spec.split('=')[0]
        installed_pkg = conda_env.installed_packages.get(pkg_name)
        assert (installed_pkg is not None,
                f'conda package {pkg_spec} from build-arg not installed')
        if '=' in pkg_spec:
            pkg_version = pkg_spec.split('=')[1]
            assert (installed_pkg.matches_version(pkg_version),
                    f'conda-installed version of package {pkg_name}, '
                    f'{installed_pkg.version} does not match build-arg '
                    f'specified version, {pkg_version}')


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
        assert (installed_pkg is not None,
                f'pip package {pkg_spec} from build-arg not installed')
        # `conda env export` command shows most recent tag for git-based
        # packages, so can't test that if installed from a commit hash
        if '=' in pkg_spec:
            pkg_version = pkg_spec.split('=')[1]
            assert (installed_pkg.matches_version(pkg_version),
                    f'pip-installed version of package {pkg_name}, '
                    f'{installed_pkg.version} does not match build-arg '
                    f'specified version, {pkg_version}')


@pytest.mark.custom_build_test
@pytest.mark.last
def test_all_custom_build_args_tested(container):
    # each custom_build_tests pops the attr tested, so none should be left
    assert len(container.expected_attrs) == 0


