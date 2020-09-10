import sys
from os import getenv
from pathlib import Path

import docker
import pytest

sys.path.insert(0, 'CI-scripts')
from image_tree import ImageTree
sys.path.pop(0)


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
            workdir=None,
            mountpoint_container=None,
            mountpoint_local=None,
            volume_mode='rw',
            port_container=None,
            port_local=None,
            name=None,
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
                                               working_dir=workdir,
                                               volumes=volumes,
                                               ports=ports,
                                               **kwargs)
        self.curr_container_obj = container
        return container


@pytest.fixture(scope='session')
def container():
    org_name = getenv("DOCKER_HUB_ORG")
    image_name = getenv("IMAGE_NAME")
    client = docker.client.from_env()
    # alternative to client.images.get() without having to know tag
    org_img_name = f'{org_name}/{image_name}'
    matching_images = client.images.list(name=org_img_name, all=False)
    assert len(matching_images) == 1, ('Found multiple images matching '
                                       f'"{org_img_name}":\n\t\t'
                                       f'{", ".join(matching_images)}')
    image = matching_images[0]
    container = Container(image)
    yield container


@pytest.fixture(scope='function', autouse=True)
def manage_containers(request, container):
    # set container name based on test function name for tracking
    test_func_name = request.function.__name__
    container.curr_container_name = f'{test_func_name}_container'
    yield

    # remove container created for test
    if container.running_container is not None:
        if container.running_container.status == 'running':
            container.running_container.stop()

        container.running_container.remove()
        container.running_container = None



def pytest_configure(config):
    config.addinivalue_line('markers', 'no_inherit_test')


def pytest_collection_modifyitems(items):
    image_name = getenv("IMAGE_NAME")
    repo_path = Path(getenv("GITHUB_WORKSPACE"))

    image_obj = ImageTree(repo_path).get_image(image_name)
    ancestor_imgs = list(map(str, image_obj.ancestors))

    skip_child_image_test = pytest.mark.skip(reason="test intended for child image")
    skip_no_inherit_test = pytest.mark.skip(reason="test restricted to parent image only")
    for item in items:
        test_native_image = Path(item.fspath).parents[2].name
        if test_native_image not in ancestor_imgs:
            item.add_marker(skip_child_image_test)
        elif (
                test_native_image != image_name and
                'no_inherit_test' in [mark.name for mark in item.own_markers]
        ):
            item.add_marker(skip_no_inherit_test)
