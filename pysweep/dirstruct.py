"""
Directory-like structures

For example, skins!
I want to be able to have .tar.gz skins,
or have the skins be directories in the fs.

Or another example, configuration files.
It would be great to attempt to load up a user specific config,
followed by a system config if not found,
and then finally fallback onto a hardcoded config.

I'm actually rather surprised python doesn't have an API for directories/archives,
only an API for files (open)...

The idea:

# Dir-like object
    >>> x = TarDir('images.tar.gz')

# Another Dir-like object
    >>> x.get('images')
    <__main__.TarDir object at ...>

# Dir-like object, but it refers to a file.
    >>> x.get('images/border/tl.png')
    <__main__.TarDir object at ...>

# You can open files by calling .open
    >>> x.get('images/border/tl.png').open()
    <ExFileObject name='images.tar.gz'>

# also works
    >>> x.get('images').get('border').get('tl.png')
    <__main__.TarDir object at ...>



# Aliases
    >>> assert x['images'] == x.get('images')
    >>> assert x.images    == x.get('images')
    >>> assert x['images']['border/tl.png'] == x.get('images').get('border/tl.png')
    >>> assert x.images.border['tl.png']    == x.get('images').get('border').get('tl.png')
"""

class Multi:
    """
    Used to get $PATH like functionality,
    so you can try the first path,
    and then the second if the first doesn't work,
    and so on.

    It's really just list comprehensions/map/filter.

    # Making a Multi
        >>> m = Multi(Dir('images_d_tiles'), Dir('images'))

    # images_d_tiles does not have borders,
    # so trying to open it gets you the one in images
        >>> m.border['b.png'].open.call_one()
        <_io.TextIOWrapper name='images/border/b.png' mode='r' encoding='UTF-8'>

    # images_d_tiles does have tiles,
    # so trying to open it gets you the one in images_d_tiles
    # since images_d_tiles comes first in the Multi.
        >>> m.board.tile['0.png'].open.call_one()
        <_io.TextIOWrapper name='images_d_tiles/board/tile/0.png' mode='r' encoding='UTF-8'>

    # If you don't use call_one,
    # it will call every item in the Multi, filtering out those that raise exceptions.
        >>> m.board.tile['0.png'].open()
        (<_io.TextIOWrapper name='images_d_tiles/board/tile/0.png' mode='r' encoding='UTF-8'>, <_io.TextIOWrapper name='images/board/tile/0.png' mode='r' encoding='UTF-8'>)
    """
    def __init__(self, *items):
        self.__multi_items = items
    def multi_map(self, map_):
        result = []
        for item in self.__multi_items:
            try:
                result.append(map_(item))
            except:
                pass
        return Multi(*result)
    def multi_filter(self, filter_):
        result = filter(filter_, self.__multi_items)
        return Multi(*result)
    def __getattr__(self, key):
        return self.multi_map(lambda item: getattr(item, key))
    def __getitem__(self, key):
        return self.multi_map(lambda item: item[key])
    def __call__(self, *args, **kwargs):
        return self.multi_map(lambda item: item(*args, **kwargs))
    def __repr__(self):
        return repr(self.__multi_items)
    def __str__(self):
        return str(self.__multi_items)
    def call_one(self, *args, **kwargs):
        for item in self.__multi_items:
            try:
                return item(*args, **kwargs)
            except:
                pass
        else:
            raise RuntimeError('None of the items could be called')
    def get_first(self):
        return self.__multi_items[0]

class DirBase:
    def __getattr__(self, path):
        return self.get(path)
    def __getitem__(self, path):
        return self.get(path)
    def get(self, path, *args, **kwargs):
        """
        Returns another object that implents DirBase.
        """
        raise NotImplementedError

    def open(self):
        """
        Returns a file-like object corresponding to the current path this dir represents
        """
        raise NotImplementedError

from pathlib import Path

class Dir(DirBase):
    def __init__(self, path=''):
        self._path = Path(path)
    def get(self, path):
        newpath = self._path.joinpath(path)
        return Dir(newpath)
    @property
    def path(self):
        return self._path
    def __fspath__(self):
        return self._path.__fspath__()
    def open(self, *args, **kwargs):
        return self._path.open(*args, **kwargs)

    def __eq__(self, other):
        return self._path == other._path

from pathlib import PurePath
import tarfile

class TarDir(DirBase):
    def __init__(self, path, *args, _tar=None, _tarpath='', _path='', **kwargs):
        if not _tar:
            self._tarpath = PurePath(_tarpath)
            self._tar = tarfile.open(path, *args, **kwargs)
            self._path = PurePath(_path)
        else:
            self._tarpath = PurePath(_tarpath)
            self._tar = _tar
            self._path = PurePath(path)
    def get(self, path):
        newpath = self._path.joinpath(path)
        return TarDir(newpath, _tar=self._tar, _tarpath=self._tarpath)
    @property
    def path(self):
        return self._path
    def __fspath__(self):
        return self._tarpath.joinpath(self._path)
    def open(self, *args, **kwargs):
        return self._tar.extractfile(str(self._path))

    def __eq__(self, other):
        return self._tar == other._tar and self._path == other._path

if __name__ == "__main__":
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
