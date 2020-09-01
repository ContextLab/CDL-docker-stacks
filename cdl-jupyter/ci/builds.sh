# functions for building various versions of image

build_default() {
    image_dir="$GITHUB_WORKSPACE/cdl-jupyter"
    docker build --rm --force-rm \
        -f "$image_dir/Dockerfile" \
        -t contextlab/cdl-jupyter:"$IMAGE_PYTHON" \
        --build-arg PYTHON_VERSION="$IMAGE_PYTHON" \
        "$image_dir"
}

