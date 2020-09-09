import sys
from os import getenv
from pathlib import Path

import docker
import pytest

sys.path.insert(0, 'CI-scripts')
from image_tree import ImageTree


class Container:
    def __init__(self):
        pass


@pytest.fixture(scope='session')
def container():
    """yields a container built from the image to be tested"""
    org_name = getenv("DOCKER_HUB_ORG")
    image_name = getenv("IMAGE_NAME")
    client = docker.client.from_env()
    # alternative to client.images.get() without having to know tag
    matching_images = client.images.list(name=f'{org_name}/{image_name}', all=False)
    assert len(matching_images) == 1
    image = matching_images[0]


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
