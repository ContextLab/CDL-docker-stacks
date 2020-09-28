#!/usr/bin/env bash

# builds the default version of an image
set -e

image_name=$1
image_dir="$GITHUB_WORKSPACE/$image_name"
images_logfile="$BUILD_DATA_DIR/images_python$PYTHON_VERSION.txt"
build_times_logfile="$BUILD_DATA_DIR/build_times_python$PYTHON_VERSION.txt"
image_sizes_logfile="$BUILD_DATA_DIR/image_sizes_python$PYTHON_VERSION.txt"
pre_flatten_tag="image-pre-flatten"

# params used for all builds (arbitrary tag for non-final image)
params="--rm --force-rm -f $image_dir/Dockerfile -t $pre_flatten_tag"

# set tag for final image & pass python version as build-arg to non-base image builds
if [[ "$image_name" == "cdl-base" ]]; then
    final_image_tag="$DOCKER_HUB_ORG/$image_name:latest"
else
    params="$params --build-arg PYTHON_VERSION"
    final_image_tag="$DOCKER_HUB_ORG/$image_name:$PYTHON_VERSION"
fi

params="$params $image_dir"

# some runner output formatting to help readability when building multiple images
term_width=$(tput cols)
printf '=%.0s' $(seq $term_width)
figlet -kw $term_width "building $image_name"

# build image and record time taken
SECONDS=0
docker build "$params"
duration=$SECONDS
echo "finished in $duration seconds"

# flatten all image layers into one to reduce size
echo "flattening image..."
docker create --name tmp_container $pre_flatten_tag &> /dev/null
docker export tmp_container | docker import - "$final_image_tag"  &> /dev/null
size_pre_flatten=$(docker image ls \
                   --filter "reference=$pre_flatten_tag" \
                   --format "{{.Size}}")
size_post_flatten=$(docker image ls \
                    --filter "reference=$final_image_tag" \
                    --format "{{.Size}}")
echo "reduced image size from $size_pre_flatten to $size_post_flatten"
docker rm tmp_container &> /dev/null
docker rmi image-pre-flatten &> /dev/null

# store some build info for later use
echo "$img" >> "$images_logfile"
echo "$duration" >> "$build_times_logfile"
echo "$size_post_flatten" >> "$image_sizes_logfile"

# more output formatting for readability
yes '' | head -n 10