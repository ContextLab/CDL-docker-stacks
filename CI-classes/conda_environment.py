import json


class CondaEnvironment:
    def __init__(self, container):
        self.container = container
        self.run_kwargs = dict(detach=False, remove=True, tty=False)
        self.config = self.parse_config()

        self.installed_packages = Permadict()
        self.requested_packages = Permadict()
        self.pinned_packages = Permadict()
        self.parse_packages()

    def parse_config(self):
        config_cmd = 'conda config --show --json'
        raw_config = self.container.run(command=config_cmd, **self.run_kwargs)
        return json.loads(raw_config)

    def parse_packages(self):
        installed_cmd = 'conda env export --name base --json --no-builds'
        requested_cmd = f'{installed_cmd} --from-history'
        raw_installed = self.container.run(command=installed_cmd, **self.run_kwargs)
        raw_requested = self.container.run(command=requested_cmd, **self.run_kwargs)
        installed = json.loads(raw_installed.decode('utf-8'))
        requested = json.loads(raw_requested.decode('utf-8'))

        for pkg_spec in installed['dependencies']:
            if isinstance(pkg_spec, dict):
                pip_specs = pkg_spec['pip']
                for pip_spec in pip_specs:
                    pkg = Package(pip_spec, installer='pip')
                    self.installed_packages[pkg.name] = pkg
            else:
                pkg = Package(pkg_spec, installer='conda')
                self.installed_packages[pkg.name] = pkg

        for pkg_spec in requested['dependencies']:
            pkg = Package(pkg_spec, installer='conda')
            self.requested_packages[pkg.name] = pkg

        for pkg_spec in self.config.get('pinned_packages'):
            pkg = Package(pkg_spec, installer=None)
            self.pinned_packages[pkg.name] = pkg


class Package:
    def __init__(self, pkg_spec, installer):
        self.installer = installer
        if self.installer == 'pip':
            self.delimiter = '=='
        else:
            self.delimiter = '='

        name_version = pkg_spec.split(self.delimiter)
        name = name_version[0]
        if len(name_version) == 1:
            version = '*'
        elif len(name_version) == 2:
            version = name_version[1]
        elif len(name_version) > 2:
            raise ValueError(f"Received unepected package spec format: {pkg_spec}")

        self.name = name
        self.major_version = None
        self.minor_version = None
        self.patch_version = None
        self.extra_labels = None
        self._parse_version(version)

    def __repr__(self):
        return f'Package({self.name}, version: {self.version}, ' \
               f'installer: {self.installer})'

    def __str__(self):
        return f'{self.name}{self.delimiter}{self.version}'

    @property
    def version(self):
        full_version = self.major_version
        if self.minor_version is not None:
            full_version += f'.{self.minor_version}'
        if self.patch_version is not None:
            full_version += f'.{self.patch_version}'
        if self.extra_labels is not None:
            full_version += self.extra_labels

        return full_version

    def _parse_version(self, version_str):
        parts = version_str.split('.')
        self.major_version = parts.pop(0)
        try:
            patch_version = ''
            self.minor_version = parts.pop(0)
            remaining = list('.'.join(parts))
            if remaining[0] == '*':
                patch_version = remaining.pop(0)

            while remaining[0].isdigit():
                patch_version += remaining.pop(0)

            self.extra_labels = ''.join(remaining)

        # pop from empty list (if no minor or patch version)
        except IndexError:
            pass
        finally:
            if patch_version != '':
                self.patch_version = patch_version

    def matches_version(self, other):
        if isinstance(other, Package):
            other_version = other.version
        else:
            other_version = other

        self_parts = self.version.split('.')
        other_parts = other_version.split('.')
        for self_part, other_part in zip(self_parts, other_parts):
            if self_part == '*' or other_part == '*':
                return True
            elif self_part != other_part:
                return False

        return True


class Permadict(dict):
    """
    dict subclass that raises an exception on setting a value for a key
    that already exists
    """
    def __setitem__(self, k, v):
        try:
            self.__getitem__(k)
            raise ValueError(f"entry for {k} already exists")
        except KeyError:
            super().__setitem__(k, v)
