def test_utf8_locale(container):
    c = container.run('echo $LANG')
    output = c.logs().decode('utf-8').strip()
    assert output == 'C.UTF-8'


def test_apt_cache_removed(container):
    output = container.run('ls --almost-all /var/lib/apt/lists',
                           detach=False,
                           remove=True)
    assert len(output) == 0
