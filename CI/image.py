class Image:
    def __init__(self, name, tree):
        self.name = name
        self.tree = tree
        self.parent = None
        self.children = list()
        self.dirpath = self.tree.root_dir.joinpath(self.name)
        # CI builds run in parallel as job matrix, divided by Python
        # version. Some images only get built for specific Python versions
        self.python_compat = True

    def __repr__(self):
        return f"Image({self.name})"

    def __str__(self):
        return self.name

    @property
    def ancestors(self):
        ancs = list()
        if self.parent is not self.tree.root_image:
            ancs.extend(self.parent.ancestors)

        ancs.append(self)
        return ancs

    @property
    def descendants(self):
        descs = list()
        for child in self.children:
            descs.extend(child.descendants)

        return [self] + descs

    def _parse_parent_from_dockerfile(self):
        def _value_from_arg(var, _dockerfile):
            # handles instance where base image can bet set via a build-arg
            var_name = var.lstrip('$')
            declaration = f'ARG {var_name}='
            arg_line = next(l for l in _dockerfile if l.startswith(declaration))
            return arg_line.replace(declaration, '')

        dockerfile = self.dirpath.joinpath('Dockerfile').read_text().splitlines()
        from_line = next(l for l in dockerfile if l.startswith('FROM'))
        parent_info = from_line.replace('FROM ', '')
        if parent_info.startswith('$'):
            parent_info = _value_from_arg(parent_info, dockerfile)

        image_tag = parent_info.replace('contextlab/', '')
        try:
            parent_image, parent_tag = image_tag.split(':')
        except ValueError:
            # tag is not explicitly set
            parent_image = image_tag
            parent_tag = None

        if (
                parent_tag is not None and
                parent_tag[0].isdigit() and
                parent_tag != self.tree.python_version
        ):
            # if the image's parent is tagged with a pinned Python
            # version, the image should only be built for that entry in
            # the job matrix
            self.python_compat = False

        return parent_image

    def add_to_tree(self):
        if self.dirpath.is_dir():
            parent_image = self._parse_parent_from_dockerfile()
            self.tree.link_images(parent=parent_image, child=self)
        else:
            self.dirpath = None
            self.tree.root_image = self

    def add_parent(self, parent):
        self.parent = parent

    def add_child(self, child):
        if child not in self.children:
            self.children.append(child)


