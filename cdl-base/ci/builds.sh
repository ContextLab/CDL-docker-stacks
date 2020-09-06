# functions for building various versions of image

build_default() {
    local image_dir="$GITHUB_WORKSPACE/cdl-base"
    docker build --rm --force-rm \
        -f "$image_dir/Dockerfile" \
        -t contextlab/cdl-base:latest \
        "$image_dir"
}

