# functions for building various versions of image
# NOTE: PsiTurk image only built and tested in Python 3.6 CI builds

build_default() {
    local image_dir="$GITHUB_WORKSPACE/cdl-psiturk"
    docker build --rm --force-rm \
        -f "$image_dir/Dockerfile" \
        -t "$DOCKER_HUB_ORG/cdl-psiturk:$PYTHON_VERSION" \
        "$image_dir"
}


build_custom() {
    local image_dir="$GITHUB_WORKSPACE/cdl-psiturk"
    # passing --build-arg without a value causes environment variable with
    # matching name to be used
    source "$GITHUB_WORKSPACE/cdl-psiturk/ci/custom-args.sh"
    docker build --rm --force-rm \
        -f "$image_dir/Dockerfile" \
        -t "$DOCKER_HUB_ORG/cdl-psiturk:${PYTHON_VERSION}-custom" \
        --build-arg APT_PACKAGES \
        --build-arg CONDA_PACKAGES \
        --build-arg PIP_VERSION \
        --build-arg PIP_PACKAGES \
        --build-arg WORKDIR \
        --build-arg MTURK \
        "$image_dir"
}