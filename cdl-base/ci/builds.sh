# functions for building various versions of image

build_default() {
  docker build --rm --force-rm -f "$GITHUB_WORKSPACE/cdl-base/Dockerfile" -t contextlab/cdl-base:latest "$GITHUB_WORKSPACE/cdl-base"
}

