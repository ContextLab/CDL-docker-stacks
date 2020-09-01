# functions for building various versions of image
# NOTE: PsiTurk image only built and tested in Python 3.6 CI builds

build_default() {
    image_dir="$GITHUB_WORKSPACE/cdl-psiturk"
    docker build --rm --force-rm \
        -f "$image_dir/Dockerfile" \
        -t contextlab/cdl-psiturk:"$IMAGE_PYTHON" \
        "$image_dir"
}