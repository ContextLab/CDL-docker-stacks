#!/usr/bin/env bash

# pushes local builds of all CDL-docker-stacks images to Docker Hub
py_version=$1
if [ -n "$py_version" ]; then
    tags=("$py_version")
else
    tags=("3.6" "3.7" "3.8")
fi

docker login

yes '' | head -n 2
echo "pushing images tagged with: ${tags[*]}"
yes '' | head -n 2

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
export repo_root=$repo_root

all_imgs=($(cd $repo_root/CI-classes && python -c "
from os import getenv
from image_tree import ImageTree
img_tree = ImageTree(getenv('repo_root'))
imgs = img_tree.all_images
print(' '.join(imgs))
"))

for img in "${all_imgs[@]}"; do
    if [[ "$img" == "cdl-base" ]]; then
        img_tags=("latest")
    else
        img_tags=("${tags[@]}")
    fi

    for tag in "${img_tags[@]}"; do
        local_imgs=$(docker image ls -q --filter "reference=contextlab/$img:$tag")
        if [ -n "$local_imgs" ]; then
            printf '=%.0s' $(seq $(tput cols))
            echo "pushing contextlab/$img:$tag..."
            echo
            docker push "contextlab/$img:$tag"
            printf '=%.0s' $(seq $(tput cols))
            yes '' | head -n 5
        fi
    done
done