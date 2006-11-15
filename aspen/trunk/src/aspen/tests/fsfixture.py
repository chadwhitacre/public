import os

def convert_path(path):
    """Given a Unix path, convert it for the current platform.
    """
    return os.sep.join(path.split('/'))

def convert_paths(paths):
    """Given a tuple of Unix paths, convert them for the current platform.
    """
    return tuple([convert_path(p) for p in paths])


def build(sitedef):
    """Return a callable that builds a filesystem fixture.

    root is the filesystem path under which to create the test site.

    sitedef is a list of strings and tuples. If a string, it is interpreted as a
    path to a directory that should be created. If a tuple, the first element is
    a path to a file, the second is the contents of the file. We do it this way
    to ease cross-platform testing.
    """
    def _build(sitedef=sitedef):
        root = 'root'
        os.mkdir(root)
        for item in sitedef:
            if isinstance(item, basestring):
                path = convert_path(item.lstrip('/'))
                path = os.sep.join([root, path])
                os.mkdir(path)
            elif isinstance(item, tuple):
                filepath, contents = item
                path = convert_path(filepath.lstrip('/'))
                path = os.sep.join([root, path])
                file(path, 'w').write(contents)
    return _build

def destroy():
    """Return a callable that destroys a filesystem fixture
    """
    root = 'root'
    if not os.path.isdir(root):
        return
    for root, dirs, files in os.walk(root, topdown=False):
        for name in dirs:
            os.rmdir(os.path.join(root, name))
        for name in files:
            os.remove(os.path.join(root, name))
    os.rmdir(root)


