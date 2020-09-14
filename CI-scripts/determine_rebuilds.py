"""
Based on Dockerfiles changed in a commit or PR, determines what
images need to be rebuilt.
Returns a list of image names (directories), sorted hierarchically so
that the builds happen in the correct order.
"""
import sys
from os import getenv
from pathlib import Path

from image_tree import ImageTree


def main():
    diff_tree_paths = sys.argv[1]
    repo_path = Path(getenv("GITHUB_WORKSPACE"))    # repo_path = Path(__file__).resolve().parents[1]
    updated_images = [path.replace('/Dockerfile', '')
                      for path in diff_tree_paths.splitlines()]
    image_tree = ImageTree(repo_path)
    to_rebuild = image_tree.determine_rebuilds(updated_images)
    # format for expansion into bash array
    return ' '.join(to_rebuild)


if __name__ == "__main__":
    sys.stdout.write(main())
