import pytest


# TODO: figure out a way to make this possible. Requires both PsiTurk
#  and AWS access keys be present in .psiturkconfig, but no way to
#  provide secure access to GitHub secrets in pull request workflows
# def test_psiturk_server():
#     pass


def test_psiturk_default_cmd(container):
    c = container.run(command=None, shell=None)
    default_cmd = c.attrs.get('Config').get('Cmd')
    assert default_cmd == ['psiturk']


@pytest.mark.custom_build_test
def test_mturk_options(container, conda_env):
    """if MTURK=true is passed as build-arg, should have pymysql installed"""
    container.expected_attrs.pop('apt_packages')
    installed_pymysql = conda_env.installed_packages.get('pymysql')
    assert installed_pymysql is not None, \
        '--build-arg MTURK=true was passed but PyMySQL is not installed'
    requested_pymysql = conda_env.requested_packages.get('pymysql')
    assert installed_pymysql.matches_version(requested_pymysql), \
        f'installed PyMySQL version ({installed_pymysql.version}) does not ' \
        f'match requested version ({requested_pymysql.version})'
