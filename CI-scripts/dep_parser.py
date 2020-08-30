"""
Based on Dockerfiles changed in a commit or PR, determines what
dependent images need to be rebuilt
"""

import sys
from os import getenv
from pathlib import Path


REPO_PATH = Path(__file__).resolve().parents[1]
IMAGE_PYTHON_VERSION = 3.6 #getenv("IMAGE_PYTHON")


class Image:
    def __init__(self, name, tree):
        self.name = name
        self.tree = tree
        self.parent = None
        self.children = list()
        self.dirpath = REPO_PATH.joinpath(self.name)
        # CI builds run in parallel as job matrix, divided by Python
        # version. Some images only get built for specific Python versions
        self.python_compat = True

    def __repr__(self):
        return self.name

    def __str__(self):
        return repr(self)

    def _parse_parent_from_dockerfile(self):
        def _value_from_arg(var, _dockerfile):
            var_name = var.lstrip('$')
            declaration = f'ARG {var_name}='
            arg_line = next(l for l in _dockerfile if l.startswith(declaration))
            return arg_line.replace(declaration, '')

        dockerfile = self.dirpath.joinpath('Dockerfile').read_text().splitlines()
        from_line = next(l for l in dockerfile if l.startswith('FROM'))
        parent_info = from_line.replace('FROM ', '')
        if parent_info.startswith('$'):
            parent_info = _value_from_arg(parent_info, dockerfile)

        image_tag = parent_info.replace('contextlab/', '')
        try:
            parent_image, parent_tag = image_tag.split(':')
        except ValueError:
            # tag is not explicitly set
            parent_image = image_tag
            parent_tag = None

        if (
                parent_tag is not None and
                parent_tag[0].isdigit() and
                parent_tag != IMAGE_PYTHON_VERSION
        ):
            # if the image's parent is tagged with a pinned Python
            # version, the image should only be built for that entry in
            # the job matrix
            self.python_compat = False

        return parent_image

    def add_to_tree(self):
        if self.dirpath.is_dir():
            parent_image = self._parse_parent_from_dockerfile()
            self.tree.link_images(parent=parent_image, child=self)
        else:
            self.dirpath = None
            self.tree.root_image = self

    def add_parent(self, parent):
        self.parent = parent

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)


class ImageTree:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.images = dict()
        self.root_image = None

        self._create_tree()

    def _create_tree(self):
        dockerfile_paths = self.root_dir.rglob('Dockerfile')
        dockerfile_paths = list(dockerfile_paths)
        for df_path in dockerfile_paths:
            image_name = df_path.parent.name
            image = self.get_image(image_name)
            image.add_to_tree()

    def get_image(self, image_name):
        try:
            return self.images[image_name]
        except KeyError:
            image = Image(image_name, tree=self)
            image.add_to_tree()
            self.images[image_name] = image
            return image

    def link_images(self, parent, child):
        if not isinstance(parent, Image):
            parent = self.get_image(parent)
        if not isinstance(child, Image):
            child = self.get_image(child)

        parent.add_child(child)
        child.add_parent(parent)

    def get_structure(self, root_image=None):
        if root_image is None:
            root_image = self.root_image
        elif not isinstance(root_image, Image):
            root_image = self.images[root_image]

        return {child: self.get_structure(child)
                for child in root_image.children}

    def determine_rebuilds(self, edited_dockerfiles):
        pass

    # def render(self, root_image=None):
    #     if root_image is None:
    #         root_image = self.root_image
    #
    #     structure = self.get_structure(root_image=root_image)
