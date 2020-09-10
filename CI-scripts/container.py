from os import getenv
from pathlib import Path

from docker.errors import NotFound


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
        # collect expected image/container attributes for testing
        self.expected_attrs = self._get_expected_attrs()

        # used by the manage_containers fixture to set container name based on
        # the currently running test function and remove all containers once
        # the test finishes
        self.curr_container_name = None
        self.curr_container_obj = None

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

                expected_attrs[attr] = value

        return expected_attrs

    def _attrs_from_dockerfile(self):
        filepath = self.image_dir.joinpath('Dockerfile')
        file_lines = filepath.read_text().splitlines()
        expected_attrs = dict()
        for line in file_lines:
            if line.startswith('ARG '):
                attr = line.replace('ARG ', '').split('=')[0]
                value = line.replace(f'ARG {attr}=', '').strip('"')
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
            expected_attrs.pop(attr)

        return expected_attrs

    def run(self,
            command,
            shell='/bin/bash',
            detach=True,
            remove=False,
            tty=True,
            max_wait=30,
            workdir=None,
            mountpoint_container=None,
            mountpoint_local=None,
            volume_mode='rw',
            port_container=None,
            port_local=None,
            **kwargs):
        if isinstance(command, str):
            command = [command]
        if workdir is None:
            workdir = self.expected_attrs.get('workdir')
        if mountpoint_container is None:
            mountpoint_container = self.expected_attrs.get('workdir', '/mnt')
        if mountpoint_local is None:
            mountpoint_local = self.default_mountpoint
        if port_container is None:
            port_container = self.expected_attrs.get('port', '8888')
        if port_local is None:
            port_local = port_container

        volumes = {
            mountpoint_local: {
                'bind': mountpoint_container,
                'mode': volume_mode
            }
        }
        ports = {port_container: port_local}
        cmd = [shell, '-c']
        cmd.extend(command)
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
        if detach:
            # if detach is True, returns a docker.containers.Container instance
            try:
                container.wait(timeout=max_wait)
            except NotFound:
                if remove:
                    pass
                else:
                    raise
            except ConnectionError as e:
                raise TimeoutError(
                    f"Command {' '.join(cmd)} during test function "
                    f"\"{self.curr_container_name.replace('_container', '')}\" "
                    f"timed out after {max_wait} seconds"
                ) from e

            if not remove:
                self.curr_container_obj = container

        else:
            # if detach is False, returns a bytes string of command's stdout
            container = container.decode('utf-8').strip()

        return container
