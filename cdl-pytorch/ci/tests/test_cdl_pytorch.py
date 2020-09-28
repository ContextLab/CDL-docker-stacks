def test_no_cuda_env_set(container):
    env = container.run('printenv', detach=False, remove=True, tty=False)
    assert 'NO_CUDA=1' in env


def test_pytorch(container):
    cmd = """
    import torch
    torch.manual_seed(0)
    x = torch.rand(5).tolist()
    for i in x:
        print(round(i, 8))
    """.replace('\n    ', '\n')
    expected = ['0.49625659', '0.7682218', '0.08847743', '0.13203049', '0.30742282']
    output = container.run(command=cmd, shell='python', detach=False, remove=True)
    result = output.splitlines()
    assert result == expected
