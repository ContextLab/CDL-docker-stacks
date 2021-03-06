import sys
from os import getenv
from pathlib import Path

import docker
import pytest


sys.path.insert(0, 'CI')
from conda_environment import CondaEnvironment
from container import Container
from image_tree import ImageTree
sys.path.pop(0)


@pytest.fixture(scope='session')
def container():
    org_name = getenv("DOCKER_HUB_ORG")
    image_name = getenv("IMAGE_NAME")
    client = docker.client.from_env()
    # alternative to client.images.get() without having to know tag
    org_img_name = f'{org_name}/{image_name}'
    matching_images = client.images.list(name=org_img_name, all=False)
    if isinstance(matching_images, docker.models.images.Image):
        matching_images = [matching_images]

    assert len(matching_images) == 1, \
        f'Found multiple images matching "{org_img_name}":\n\t\t' \
        f'{", ".join([t for img in matching_images for t in img.tags])}'

    image = matching_images[0]
    container = Container(image)
    yield container


@pytest.fixture(scope='session')
def conda_env(container):
    environment = CondaEnvironment(container)
    yield environment


@pytest.fixture(scope='function', autouse=True)
def manage_containers(request, container):
    # set container name based on test function name for tracking
    test_func_name = request.function.__name__
    container.curr_container_name = f'{test_func_name}_container'
    yield

    # remove container created during test function if:
    # A) one was created at all, and
    # B) it was run with remove=False
    if container.curr_container_obj is not None:
        try:
            try:
                container.curr_container_obj.stop()
            except docker.errors.NotFound:
                # container was stopped in test function body
                pass

            container.curr_container_obj.remove()

        except (docker.errors.APIError, docker.errors.NotFound):
            # container was removed in test function body
            pass

        container.curr_container_obj = None


def pytest_configure(config):
    config.addinivalue_line('markers', 'child_image_test')
    config.addinivalue_line('markers', 'no_inherit_test')
    config.addinivalue_line('markers', 'custom_build_test')


def pytest_collection_modifyitems(items):
    image_name = getenv("IMAGE_NAME")
    build_style = getenv("BUILD_STYLE")
    repo_path = Path(getenv("GITHUB_WORKSPACE"))

    image_obj = ImageTree(repo_path).get_image(image_name)
    ancestor_imgs = list(map(str, image_obj.ancestors))

    skip_child_image_test = pytest.mark.skip(reason="test intended for child image")
    skip_no_inherit_test = pytest.mark.skip(reason="test restricted to parent image only")
    skip_custom_build_test = pytest.mark.skip(reason="test restricted to custom-build tests")
    for item in items:
        test_native_image = Path(item.fspath).parents[2].name
        if test_native_image not in ancestor_imgs:
            item.add_marker(skip_child_image_test)
        elif (
                test_native_image != image_name and
                'no_inherit_test' in [mark.name for mark in item.own_markers]
        ):
            item.add_marker(skip_no_inherit_test)
        elif (
                build_style != 'custom' and
                'custom_build_test' in [mark.name for mark in item.own_markers]
        ):
            item.add_marker(skip_custom_build_test)
