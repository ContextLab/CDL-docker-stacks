# pins the currently installed version of a conda package and its related
# packages (e.g., numpy, numpy-base), overwriting the existing pinned versions
# if they exists

pin_package() {
    if [[ "$2" == "major" ]]; then
        local n_fields=1
    elif [[ "$2" == "minor" ]]; then
        local n_fields=1,2
    fi

    # shellcheck disable=SC2207
    local pkgs_to_pin=($(conda list "$1" \
        | grep "^$1" \
        | tr -s ' ' \
        | cut -d ' ' -f 1,2 \
        | cut -d '.' -f $n_fields \
        | sed 's/$/.*/g; s/ /=/g'))

    for pkg_spec in "${pkgs_to_pin[@]}"; do
        local search_str="$(echo "$pkg_spec" | cut -d '=' -f 1)="
        local curr_pinned_version=$(conda config --show pinned_packages \
            | grep "^  - $search_str" \
            | tr -d ' -')
        if [ -n "$curr_pinned_version" ]; then
            conda config --remove pinned_packages "$curr_pinned_version"
        fi
        conda config --add pinned_packages "$pkg_spec"
    done
}