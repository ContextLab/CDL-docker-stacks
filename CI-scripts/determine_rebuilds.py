"""
Based on Dockerfiles changed in a commit or PR, determines what
images need to be rebuilt.
Returns a list of image names (directories), sorted hierarchically so
that the builds happen in the correct order.
"""


import sys
from pathlib import Path

from image_tree import ImageTree


def determine_rebuilds(tree, edited_names):
    dependent_imgs = list()
    for name in edited_names:
        try:
            image = tree.images[name]
        except KeyError as e:
            raise ValueError(f"Couldn't find an image named \"{name}\" "
                             f"in:\n{', '.join(tree.images.keys())}") from e

        dependent_imgs.extend(image.descendants)

    images_unique = list(set(dependent_imgs))
    # sort by number of intermediate parents between image and root_image
    images_sorted = sorted(images_unique, key=lambda img: len(img.ancestors))
    to_rebuild = [img.name for img in images_sorted if img.python_compat]
    return to_rebuild


def main():
    repo_path = Path(__file__).resolve().parents[1]
    diff_tree_paths = sys.argv[1]
    updated_images = [path.replace('/Dockerfile', '')
                      for path in diff_tree_paths.splitlines()]
    image_tree = ImageTree(repo_path)
    to_rebuild = determine_rebuilds(image_tree, updated_images)
    return to_rebuild


if __name__ == "__main__":
    print(main())
