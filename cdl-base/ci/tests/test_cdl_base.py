def test_utf8_locale(container):
    c = container.run('echo $LANG')
    output = c.logs().decode('utf-8').strip()
    assert output == 'C.UTF-8'


def test_apt_cache_removed(container):
    c = container.run('ls --almost-all /var/lib/apt/lists')
    output = c.logs().decode('utf-8').strip()
    assert len(output) == 0
