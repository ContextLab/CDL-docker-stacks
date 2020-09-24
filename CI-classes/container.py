from os import getenv
from pathlib import Path

import docker
import requests


class Container:
    def __init__(self, image):
        self.image = image
        self.client = self.image.client
        self.image_name_full = self.image.tags[0]
        self.image_name = self.image_name_full.split('/')[-1].split(':')[0]
        self.image_tag = self.image_name_full.split(':')[-1]
        self.owner = self.image_name_full.split('/')[0]
        self.custom_build = self.image_tag.endswith('custom')

        self.default_mountpoint = getenv("GITHUB_WORKSPACE")
        self.image_dir = Path(self.default_mountpoint).joinpath(self.image_name)
        # used by the manage_containers fixture to set container name
        # based on the currently running test function and remove all
        # containers once the test finishes
        self.curr_container_name = None
        self.curr_container_obj = None
        # collect expected image/container attributes for testing
        self.expected_attrs = self._get_expected_attrs()
        # parse installed apt packages for testing
        self.apt_packages = self._get_apt_packages()

    def _attrs_from_custom_args(self):
        filepath = self.image_dir.joinpath('ci', 'custom-args.sh')
        file_lines = filepath.read_text().splitlines()
        expected_attrs = dict()

        for line in file_lines:
            if line.startswith('export '):
                attr = line.replace('export ', '').split('=')[0]
                value = line.replace(f'export {attr}=', '').strip('"')
                if ' ' in value:
                    value = value.split()
                elif value == 'true':
                    value = True
                elif value == 'false':
                    value = False

                expected_attrs[attr.lower()] = value

        return expected_attrs

    def _attrs_from_dockerfile(self):
        filepath = self.image_dir.joinpath('Dockerfile')
        file_lines = filepath.read_text().splitlines()
        expected_attrs = dict()
        for line in file_lines:
            if line.startswith('ARG '):
                attr = line.replace('ARG ', '').split('=')[0]
                value = line.replace(f'ARG {attr}=', '').strip('"')
                if value == 'true':
                    value = True
                elif value == 'false':
                    value = False

                expected_attrs[attr.lower()] = value

        return expected_attrs

    def _get_expected_attrs(self):
        # ARG lines in Dockerfile to be excluded from tests
        attrs_ignore = ['base_image', 'debian_frontend', 'notebook_ip']
        expected_attrs = self._attrs_from_dockerfile()
        if self.custom_build:
            custom_attrs = self._attrs_from_custom_args()
            expected_attrs.update(custom_attrs)

        for attr in attrs_ignore:
            if attr in expected_attrs.keys():
                expected_attrs.pop(attr)

        empty_attrs = [attr for attr, val in expected_attrs.items() if val == '']
        for attr in empty_attrs:
            expected_attrs.pop(attr)

        return expected_attrs

    def _get_apt_packages(self):
        apt_log = self.run('cat /var/log/apt/history.log',
                           detach=False,
                           remove=True)
        apt_packages = dict()
        for line in apt_log.splitlines():
            if line.startswith('Install:'):
                packages = line.replace('Install: ', '').split('), ')
                for pkg_spec in packages:
                    pkg_name = pkg_spec.split(':')[0]
                    if pkg_spec.endswith('automatic'):
                        install_method = 'automatic'
                    else:
                        install_method = 'manual'
                    apt_packages[pkg_name] = install_method

        return apt_packages

    def run(self,
            command=None,
            shell='/bin/bash',
            shell_flags='-c',
            detach=True,
            remove=False,
            tty=True,
            max_wait=30,
            workdir=None,
            mount=False,
            mountpoint_container=None,
            mountpoint_local=None,
            volume_mode='rw',
            publish_port=False,
            port_container=None,
            port_local=None,
            **kwargs):
        if workdir is None:
            workdir = self.expected_attrs.get('workdir')
        if mountpoint_container is not None or mountpoint_local is not None:
            mount = True
        if port_container is not None or port_local is not None:
            publish_port = True

        if mount:
            if mountpoint_container is None:
                mountpoint_container = self.expected_attrs.get('workdir', '/mnt')
            if mountpoint_local is None:
                mountpoint_local = self.default_mountpoint
            volumes = {
                mountpoint_local: {
                    'bind': mountpoint_container,
                    'mode': volume_mode
                }
            }
        else:
            volumes = None

        if publish_port:
            if port_container is None:
                port_container = self.expected_attrs.get('port', '8888')
            if port_local is None:
                port_local = port_container
            ports = {port_container: port_local}
        else:
            ports = None

        if command is not None:
            cmd = [shell]
            if shell_flags is not None:
                if isinstance(shell_flags, str):
                    shell_flags = shell_flags.split()

                cmd.extend(shell_flags)

            if isinstance(command, str):
                command = [command]

            cmd.extend(command)
        else:
            cmd = None
            
        container = self.client.containers.run(self.image_name_full,
                                               command=cmd,
                                               name=self.curr_container_name,
                                               detach=detach,
                                               remove=remove,
                                               tty=tty,
                                               working_dir=workdir,
                                               volumes=volumes,
                                               ports=ports,
                                               **kwargs)
        # if detach is True, returns a docker.containers.Container instance
        if detach:
            # set max_wait to -1 to return without waiting
            # (e.g., when testing notebook server)
            if max_wait >= 0:
                try:
                    container.wait(timeout=max_wait)
                except docker.errors.NotFound:
                    # unlikely to happen, but would be raised if remove is
                    # True and container was removed before container.wait()
                    # was called
                    if remove:
                        pass
                    else:
                        raise
                except requests.ConnectionError as e:
                    # command didn't finish running in max_wait seconds
                    _cmd = '' if cmd is None else ''.join(cmd)
                    raise TimeoutError(
                        f"Command {_cmd} during test function "
                        f"\"{self.curr_container_name.replace('_container', '')}\" "
                        f"timed out after {max_wait} seconds"
                    ) from e

            if not remove:
                # if container isn't removed here (so it can be used
                # later in same test function), this causes it to be
                # removed by the manage_containers fixture after the
                # test function returns
                self.curr_container_obj = container
        else:
            # if detach is False, decode the bytes string of command's
            # stdout before returning for convenience
            container = container.decode('utf-8').strip()

        return container
