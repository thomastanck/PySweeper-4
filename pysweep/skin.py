from pathlib import PurePath

from PIL import Image

from .dirstruct import Multi, DirBase

class ImageLoader(DirBase):
    """
    Wraps around a Dir-like or a Multi and tries to load files as images.

        >>> from .dirstruct import Multi, Dir, TarDir

    # Input a Multi and ImageLoader will make PIL images out of them.
        >>> il = ImageLoader(Multi(Dir('images_d_tiles'), TarDir('images.tar.gz').images))

        >>> il.border['b.png'].open()
        <PIL.PngImagePlugin.PngImageFile image mode=RGBA size=1x9 at 0x...>

        >>> il.board.tile['0.png'].open()
        <PIL.PngImagePlugin.PngImageFile image mode=RGBA size=32x32 at 0x...>

    # Works directly with Dir-like objects too.
        >>> il2 = ImageLoader(TarDir('images.tar.gz').images)
        >>> il2.border['b.png'].open()
        <PIL.PngImagePlugin.PngImageFile image mode=RGBA size=1x9 at 0x...>

        >>> il3 = ImageLoader(Dir('images'))
        >>> il3.border['b.png'].open()
        <PIL.PngImagePlugin.PngImageFile image mode=RGBA size=1x9 at 0x...>

    # Global cache
        >>> assert len(ImageLoader._cache) == len(il.cache) == len(il2.cache) == len(il3.cache) == 4

    # Preload the files you need
        >>> il.preload('border/b.png', 'border/t.png') # And a lot more
        >>> il.cache[(il._source, PurePath('border/t.png'))]
        <PIL.PngImagePlugin.PngImageFile image mode=RGBA size=1x9 at 0x...>
        >>> assert len(il.cache) == len(il2.cache) == len(il3.cache) == 5
    """
    _cache = {} # Map of (source: Multi or Dir-like, path: Path-like) to img: Image

    @property
    def cache(self):
        return ImageLoader._cache
    @cache.setter
    def cache(self, value):
        ImageLoader._cache = value

    def __init__(self, source, path=''):
        self._source = source
        self._path = PurePath(path)
    def get(self, path):
        newpath = self._path.joinpath(path)
        return ImageLoader(self._source, newpath)
    def open(self):
        try:
            return self.cache[(self._source, self._path)]
        except KeyError:
            loc = self._source.get(self._path)
            if isinstance(loc, Multi):
                img = loc.multi_map_one(lambda l: Image.open(l.open('rb')))
            elif isinstance(loc, DirBase):
                img = Image.open(loc.open('rb'))
            else:
                raise TypeError('source was not Multi or DirBase')
            self.cache[(self._source, self._path)] = img
            return img

    def preload(self, *paths):
        for path in paths:
            self.get(path).open()

class ValidationException(Exception):
    pass
class SpriteException(ValidationException):
    pass
class BorderException(ValidationException):
    pass

class Skin(ImageLoader):
    """
    ImageLoader with some functions specific to PySweeper skins,
    preload_skin loads all skinnable images,
    and validate_skin checks all image sizes.

        >>> from .dirstruct import Multi, Dir, TarDir
        >>> skin = Skin(Multi(Dir('images_d_tiles'), TarDir('images.tar.gz').images))

    # Reset the global cache for testing purposes.
        >>> skin.cache = {}
        >>> len(skin.cache)
        0

    # Check number of images are correct
        >>> skin.preload_skin()
        >>> len(skin.cache)
        85

    # Proof that preloading really works
        >>> skin.cache = {}
        >>> len(skin.cache)
        0
        >>> skin.border['t.png'].open()
        <PIL.PngImagePlugin.PngImageFile image mode=RGBA size=1x9 at 0x...>
        >>> len(skin.cache)
        1
        >>> skin.preload_skin()
        >>> len(skin.cache)
        85
        >>> skin.border['t.png'].open()
        <PIL.PngImagePlugin.PngImageFile image mode=RGBA size=1x9 at 0x...>
        >>> len(skin.cache)
        85

    # Validate skin
        >>> skin.validate_skin() # Should not raise exception

        >>> skin = Skin(Dir('images_wrong'))
        >>> skin.validate_skin() # Should raise exception
        Traceback (most recent call last):
          ...
        ValueError: (\
'Skin validation failed.', \
"All borders must have consistent thickness. Expected height 9 from border/bl.png but 'border/b.png' has height 1.", \
"Sprites must be of the same size. Expected size (26, 26) from 'panel/face/blast.png', but 'panel/face/cool.png' has size (16, 16).")
    """
    def preload_skin(self):
        self.preload(
            'board/bg.png',
            'board/border/b.png',
            'board/border/bl.png',
            'board/border/br.png',
            'board/border/l.png',
            'board/border/r.png',
            'board/border/t.png',
            'board/border/tl.png',
            'board/border/tr.png',
            'board/tile/0.png',
            'board/tile/1.png',
            'board/tile/2.png',
            'board/tile/3.png',
            'board/tile/4.png',
            'board/tile/5.png',
            'board/tile/6.png',
            'board/tile/7.png',
            'board/tile/8.png',
            'board/tile/blast.png',
            'board/tile/flag.png',
            'board/tile/flag_wrong.png',
            'board/tile/mine.png',
            'board/tile/unopened.png',
            'border/b.png',
            'border/bl.png',
            'border/br.png',
            'border/l.png',
            'border/r.png',
            'border/t.png',
            'border/tl.png',
            'border/tr.png',
            'panel/bg.png',
            'panel/border/b.png',
            'panel/border/bl.png',
            'panel/border/br.png',
            'panel/border/l.png',
            'panel/border/r.png',
            'panel/border/t.png',
            'panel/border/tl.png',
            'panel/border/tr.png',
            'panel/face/blast.png',
            'panel/face/cool.png',
            'panel/face/happy.png',
            'panel/face/nervous.png',
            'panel/face/pressed.png',
            'panel/lcounter/border/b.png',
            'panel/lcounter/border/bl.png',
            'panel/lcounter/border/br.png',
            'panel/lcounter/border/l.png',
            'panel/lcounter/border/r.png',
            'panel/lcounter/border/t.png',
            'panel/lcounter/border/tl.png',
            'panel/lcounter/border/tr.png',
            'panel/lcounter/digit/-.png',
            'panel/lcounter/digit/0.png',
            'panel/lcounter/digit/1.png',
            'panel/lcounter/digit/2.png',
            'panel/lcounter/digit/3.png',
            'panel/lcounter/digit/4.png',
            'panel/lcounter/digit/5.png',
            'panel/lcounter/digit/6.png',
            'panel/lcounter/digit/7.png',
            'panel/lcounter/digit/8.png',
            'panel/lcounter/digit/9.png',
            'panel/lcounter/digit/off.png',
            'panel/rcounter/border/b.png',
            'panel/rcounter/border/bl.png',
            'panel/rcounter/border/br.png',
            'panel/rcounter/border/l.png',
            'panel/rcounter/border/r.png',
            'panel/rcounter/border/t.png',
            'panel/rcounter/border/tl.png',
            'panel/rcounter/border/tr.png',
            'panel/rcounter/digit/-.png',
            'panel/rcounter/digit/0.png',
            'panel/rcounter/digit/1.png',
            'panel/rcounter/digit/2.png',
            'panel/rcounter/digit/3.png',
            'panel/rcounter/digit/4.png',
            'panel/rcounter/digit/5.png',
            'panel/rcounter/digit/6.png',
            'panel/rcounter/digit/7.png',
            'panel/rcounter/digit/8.png',
            'panel/rcounter/digit/9.png',
            'panel/rcounter/digit/off.png',
        )

    def validate_skin(self):
        exceptions = []
                #'board/bg.png',
        try:
            self._validate_border(
                'board/border/b.png',
                'board/border/bl.png',
                'board/border/br.png',
                'board/border/l.png',
                'board/border/r.png',
                'board/border/t.png',
                'board/border/tl.png',
                'board/border/tr.png',
            )
        except ValidationException as e:
            exceptions.append(str(e))
        try:
            self._validate_sprite(
                'board/tile/0.png',
                'board/tile/1.png',
                'board/tile/2.png',
                'board/tile/3.png',
                'board/tile/4.png',
                'board/tile/5.png',
                'board/tile/6.png',
                'board/tile/7.png',
                'board/tile/8.png',
                'board/tile/blast.png',
                'board/tile/flag.png',
                'board/tile/flag_wrong.png',
                'board/tile/mine.png',
                'board/tile/unopened.png',
            )
        except ValidationException as e:
            exceptions.append(str(e))
        try:
            self._validate_border(
                'border/b.png',
                'border/bl.png',
                'border/br.png',
                'border/l.png',
                'border/r.png',
                'border/t.png',
                'border/tl.png',
                'border/tr.png',
            )
                #'panel/bg.png',
        except ValidationException as e:
            exceptions.append(str(e))
        try:
            self._validate_border(
                'panel/border/b.png',
                'panel/border/bl.png',
                'panel/border/br.png',
                'panel/border/l.png',
                'panel/border/r.png',
                'panel/border/t.png',
                'panel/border/tl.png',
                'panel/border/tr.png',
            )
        except ValidationException as e:
            exceptions.append(str(e))
        try:
            self._validate_sprite(
                'panel/face/blast.png',
                'panel/face/cool.png',
                'panel/face/happy.png',
                'panel/face/nervous.png',
                'panel/face/pressed.png',
            )
        except ValidationException as e:
            exceptions.append(str(e))
        try:
            self._validate_border(
                'panel/lcounter/border/b.png',
                'panel/lcounter/border/bl.png',
                'panel/lcounter/border/br.png',
                'panel/lcounter/border/l.png',
                'panel/lcounter/border/r.png',
                'panel/lcounter/border/t.png',
                'panel/lcounter/border/tl.png',
                'panel/lcounter/border/tr.png',
            )
        except ValidationException as e:
            exceptions.append(str(e))
        try:
            self._validate_sprite(
                'panel/lcounter/digit/-.png',
                'panel/lcounter/digit/0.png',
                'panel/lcounter/digit/1.png',
                'panel/lcounter/digit/2.png',
                'panel/lcounter/digit/3.png',
                'panel/lcounter/digit/4.png',
                'panel/lcounter/digit/5.png',
                'panel/lcounter/digit/6.png',
                'panel/lcounter/digit/7.png',
                'panel/lcounter/digit/8.png',
                'panel/lcounter/digit/9.png',
                'panel/lcounter/digit/off.png',
            )
        except ValidationException as e:
            exceptions.append(str(e))
        try:
            self._validate_border(
                'panel/rcounter/border/b.png',
                'panel/rcounter/border/bl.png',
                'panel/rcounter/border/br.png',
                'panel/rcounter/border/l.png',
                'panel/rcounter/border/r.png',
                'panel/rcounter/border/t.png',
                'panel/rcounter/border/tl.png',
                'panel/rcounter/border/tr.png',
            )
        except ValidationException as e:
            exceptions.append(str(e))
        try:
            self._validate_sprite(
                'panel/rcounter/digit/-.png',
                'panel/rcounter/digit/0.png',
                'panel/rcounter/digit/1.png',
                'panel/rcounter/digit/2.png',
                'panel/rcounter/digit/3.png',
                'panel/rcounter/digit/4.png',
                'panel/rcounter/digit/5.png',
                'panel/rcounter/digit/6.png',
                'panel/rcounter/digit/7.png',
                'panel/rcounter/digit/8.png',
                'panel/rcounter/digit/9.png',
                'panel/rcounter/digit/off.png',
            )
        except ValidationException as e:
            exceptions.append(str(e))
        if len(exceptions) > 0:
            raise ValueError('Skin validation failed.', *exceptions)

    def _validate_sprite(self, *spritepaths):
        size = None
        firstpath = None
        for path in spritepaths:
            img = self[path].open()

            if size == None:
                size = img.size
                firstpath = path
            else:
                try:
                    assert size == img.size
                except AssertionError as e:
                    raise SpriteException(f'''Sprites must be of the same size. Expected size {size} from '{firstpath}', but '{path}' has size {img.size}.''')

    def _validate_border(self, b, bl, br, l, r, t, tl, tr):
        thickness = [None] * 4
        # Check top size
        for key in (tl, t, tr):
            img = self[key].open()
            if thickness[0] == None:
                thickness[0] = img.size[1]
                firstpath = key
            else:
                try:
                    assert thickness[0] == img.size[1]
                except AssertionError as e:
                    raise BorderException(f'''All borders must have consistent thickness. Expected height {thickness[0]} from {firstpath} but '{key}' has height {img.size[1]}.''')
        # Check left size
        for key in (tl, l, bl):
            img = self[key].open()
            if thickness[1] == None:
                thickness[1] = img.size[0]
                firstpath = key
            else:
                try:
                    assert thickness[1] == img.size[0]
                except AssertionError as e:
                    raise BorderException(f'''All borders must have consistent thickness. Expected width {thickness[1]} from {firstpath} but '{key}' has width {img.size[0]}.''')
        # Check right size
        for key in (tr, r, br):
            img = self[key].open()
            if thickness[2] == None:
                thickness[2] = img.size[0]
                firstpath = key
            else:
                try:
                    assert thickness[2] == img.size[0]
                except AssertionError as e:
                    raise BorderException(f'''All borders must have consistent thickness. Expected width {thickness[2]} from {firstpath} but '{key}' has width {img.size[0]}.''')
        # Check bottom size
        for key in (bl, b, br):
            img = self[key].open()
            if thickness[3] == None:
                thickness[3] = img.size[1]
                firstpath = key
            else:
                try:
                    assert thickness[3] == img.size[1]
                except AssertionError as e:
                    raise BorderException(f'''All borders must have consistent thickness. Expected height {thickness[3]} from {firstpath} but '{key}' has height {img.size[1]}.''')


if __name__ == "__main__":
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
