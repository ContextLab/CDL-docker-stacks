#!/usr/bin/env bash

# builds the default version of an image
set -e

image_name=$1
image_dir="$GITHUB_WORKSPACE/$image_name"
images_logfile="$BUILD_DATA_DIR/images_python$PYTHON_VERSION.txt"
build_times_logfile="$BUILD_DATA_DIR/build_times_python$PYTHON_VERSION.txt"
image_sizes_logfile="$BUILD_DATA_DIR/image_sizes_python$PYTHON_VERSION.txt"

# params used for all builds (arbitrary tag for non-final image)
params="--rm --force-rm --squash -f $image_dir/Dockerfile"

# set tag for image & pass python version as build-arg to non-base image builds
if [[ "$image_name" == "cdl-base" ]]; then
    image_tag="$DOCKER_HUB_ORG/$image_name:latest"
else
    image_tag="$DOCKER_HUB_ORG/$image_name:$PYTHON_VERSION"
    params="$params --build-arg PYTHON_VERSION"
fi

params="$params -t $image_tag $image_dir"

# some runner output formatting to help readability when building multiple images
term_width=$(tput cols)
printf '=%.0s' $(seq $term_width)
echo
figlet -kw $term_width "building $image_name"

# build image, record time taken & final size
SECONDS=0
docker build $params
duration=$SECONDS
echo "finished in $duration seconds"

image_size=$(docker image ls --filter "reference=$image_tag" --format "{{.Size}}")
echo "resulting image size is $image_size"

# store some build info for later use
echo "$image_name" >> "$images_logfile"
echo "$duration" >> "$build_times_logfile"
echo "$image_size" >> "$image_sizes_logfile"

# more output formatting for readability
yes '' | head -n 10