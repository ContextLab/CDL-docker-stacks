#!/usr/bin/env bash

# builds custom variant of an image for testing
set -e

image_name=$1
image_dir="$GITHUB_WORKSPACE/$image_name"
custom_args_file="$image_dir/ci/custom-args.sh"

# params used for all custom builds
params="--rm --force-rm
        -f $image_dir/Dockerfile
        -t $DOCKER_HUB_ORG/$image_name:${PYTHON_VERSION}-custom
        --build-arg PYTHON_VERSION"

# get custom arg names from file
custom_args=($(grep ^export $custom_args_file | cut -d ' ' -f 2 | cut -d '=' -f 1))

for arg in "${custom_args[@]}"; do
    params="$params --build-arg $arg"
done

params="$params $image_dir"

source $custom_args_file
docker build "$params"