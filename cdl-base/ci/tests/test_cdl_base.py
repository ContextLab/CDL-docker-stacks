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
def test_utf8_locale(container):
    c = container.run('echo $LANG')
    output = c.logs().decode('utf-8').strip()
    assert output == 'C.UTF-8'


def test_apt_packages_installed(container):
    for apt_pkg in CDL_BASE_APT_PACKAGES:
        pkg_installed = container.apt_packages.get(apt_pkg)
        assert pkg_installed is not None, f'{apt_pkg} is not installed'
        assert (pkg_installed == 'manual',
                f'{apt_pkg} was installed as a dependency of another package, '
                'not manually')


def test_apt_cache_removed(container):
    output = container.run('ls --almost-all /var/lib/apt/lists',
                           detach=False,
                           remove=True)
    assert len(output) == 0
