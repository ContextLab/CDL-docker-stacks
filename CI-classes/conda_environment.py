import json
from packaging.specifiers import Specifier


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
        installed = json.loads(raw_installed)
        requested = json.loads(raw_requested)

        for pkg_spec in installed['dependencies']:
            if isinstance(pkg_spec, dict):
                pip_specs = pkg_spec['pip']
                for pip_spec in pip_specs:
                    pkg = Package(pip_spec)
                    self.installed_packages[pkg.name] = pkg
            else:
                pkg = Package(pkg_spec)
                self.installed_packages[pkg.name] = pkg

        for pkg_spec in requested['dependencies']:
            pkg = Package(pkg_spec)
            self.requested_packages[pkg.name] = pkg

        for pkg_spec in self.config.get('pinned_packages'):
            pkg = Package(pkg_spec)
            self.pinned_packages[pkg.name] = pkg


class Package:
    def __init__(self, pkg_spec):
        self.name = None
        self.major_version = None
        self.minor_version = None
        self.patch_version = None
        self.extra_labels = None

        for spec_delim in ['==', '<=', '>=', '!=', '~=', '<', '>', '=']:
            if spec_delim in pkg_spec:
                self.delimiter = spec_delim
                name, version = pkg_spec.split(self.delimiter)
                self.name = name
                self._parse_version(version)
                break
        else:
            # just package name, no specifier
            self.delimiter = None

    def __repr__(self):
        return f'Package({str(self)})'

    def __str__(self):
        if self.delimiter is None:
            return self.name
        else:
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
        except IndexError:
            # popped from empty list (if no minor or patch version)
            pass
        finally:
            if patch_version != '':
                self.patch_version = patch_version

    def matches_version(self, other):
        """
        returns true of self.version fits within the specification
        given by other.version
        """
        if not isinstance(other, Package):
            other = Package(other)

        if other.version is None or other.version == '*':
            return True
        elif other.delimiter == '=':
            other_delim = '=='
        else:
            other_delim = other.delimiter

        if (
                other_delim in ('==', '!=') and
                (other.minor_version is None or other.patch_version is None) and
                not other.version.endswith('.*')
        ):
            other_version = f'{other.version}.*'
        elif other_delim not in ('==', '!=') and other.version.endswith('.*'):
            other_version = other.version.split('.*')[0]
        else:
            other_version = other.version

        other_spec = Specifier(f'{other_delim}{other_version}')
        return other_spec.contains(self.version)


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
