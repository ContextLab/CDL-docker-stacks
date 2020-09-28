"""
Implements a simple m-ary tree of image dependencies
"""
from os import getenv
from pathlib import Path

from image import Image


class ImageTree:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.images = dict()
        self.root_image = None
        self.python_version = getenv("PYTHON_VERSION")

        self._create_tree()

    def _create_tree(self):
        dockerfile_paths = self.root_dir.rglob('Dockerfile')
        dockerfile_paths = list(dockerfile_paths)
        for df_path in dockerfile_paths:
            image_name = df_path.parent.name
            image = self.get_image(image_name, create_new=True)
            image.add_to_tree()

    @property
    def all_images(self):
        return self.get_dependents(self.root_image.children[0])

    def create_image(self, image_name):
        image = Image(image_name, tree=self)
        image.add_to_tree()
        self.images[image_name] = image
        return image

    def get_dependents(self, edited_img_names):
        if isinstance(edited_img_names, str):
            edited_img_names = [edited_img_names]
        elif isinstance(edited_img_names, Image):
            edited_img_names = [str(edited_img_names)]

        dependent_imgs = list()
        for img_name in edited_img_names:
            # image must exist at this point, or raise error
            image = self.get_image(img_name, create_new=False)
            dependent_imgs.extend(image.descendants)

        unique_deps = list(set(dependent_imgs))
        # sort by number of intermediate parents between image and self.root_image
        sorted_deps = sorted(unique_deps, key=lambda img: len(img.ancestors))
        # filter out images not compatible with current CI build's Python version
        compat_deps = [img.name for img in sorted_deps if img.python_compat]
        return compat_deps

    def get_image(self, image_name, create_new=False):
        try:
            return self.images[image_name]
        except KeyError as e:
            if create_new:
                return self.create_image(image_name)
            else:
                raise ValueError(f"No Image named {image_name} "
                                 f"in:{', '.join(self.images.keys())}") from e

    def link_images(self, parent, child):
        if not isinstance(parent, Image):
            parent = self.get_image(parent, create_new=True)
        if not isinstance(child, Image):
            child = self.get_image(child, create_new=True)

        if not parent.python_compat:
            child.python_compat = False

        parent.add_child(child)
        child.add_parent(parent)

    # def get_structure(self, root_image=None):
    #     if root_image is None:
    #         root_image = self.root_image
    #     elif not isinstance(root_image, Image):
    #         root_image = self.images[root_image]
    #
    #     return {child: self.get_structure(child)
    #             for child in root_image.children}

    # def render(self, root_image=None):
    #     if root_image is None:
    #         root_image = self.root_image
    #
    #     structure = self.get_structure(root_image=root_image)
