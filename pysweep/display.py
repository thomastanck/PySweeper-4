from enum import Enum, auto
from .box import Thickness, Box, GridBox, LayerBox, BorderBox

""" Errors """

class NotExpandableError(Exception):
    pass

""" State Enums """

class DigitState:
    class Off: name = 'off.png'
    class Minus: name = '-.png'
    # A bit of magic to create 10 classes of 'Digit' in an array
    # You use this like DigitState.Digit[i] where i=0..9
    Digit = [type('Digit_{}'.format(i),
                   (),
                   {'n': i, 'name': f'{i}.png'})
              for i in range(10)]

class FaceState:
    class Happy: name = 'happy.png'
    class Pressed: name = 'pressed.png'
    class Blast: name = 'blast.png'
    class Cool: name = 'cool.png'
    class Nervous: name = 'nervous.png'

class TileState:
    """
    enum for a tile's state

    Seems easier to use than an actual Enum
    because of the Number[0] syntax.
    """
    class Mine: name = 'mine.png'
    class Blast: name = 'blast.png'
    class Flag: name = 'flag.png'
    class FlagWrong: name = 'flagwrong.png'
    class Unopened: name = 'unopened.png'
    # A bit of magic to create 9 classes of 'Number' in an array
    # You use this like TileState.Number[i] where i=0..8
    Number = [type('Number_{}'.format(i),
                   (),
                   {'n': i, 'name': f'{i}.png'})
              for i in range(9)]

""" DisplayImage """

class DisplayImage:
    """
    Image objects are passed into these parts as the first arg,
    and they call .paste to paste images into this 'image'.
    """
    def __init__(self, pil_image):
        self.pil_image = pil_image

    def paste(self, img, coords):
        self.pil_image.paste(img, coords, img)

    def paste_pixel(self, pixel, coords):
        self.pil_image.paste(pixel, coords)

""" Drawing classes """

class GridTile(Box):
    """ Tiles the image over the entire area """
    class PasteType(Enum):
        Tile     = auto() # Tile in both directions (default)
        Horz     = auto() # Tile in horizontal direction
        Vert     = auto() # Tile in vertical direction
        Once     = auto() # Don't tile

        TileFast = auto() # Optimisation for when the image itself is 1x1
        HorzFast = auto() # Optimisation for when image is 1xh (resize width)
        VertFast = auto() # Optimisation for when image is wx1 (resize height)

    def __init__(self, image, skin, pastetype=None, expandfactor=1):
        self.image, self.skin = image, skin

        Type = GridTile.PasteType

        if pastetype is None:
            pastetype = Type.Tile

        self.tileimg = skin.open()

        Box.__init__(self, *self.tileimg.size, expandfactor=expandfactor)

        # Detect optimisations
        if pastetype == Type.Tile and self.tileimg.size == (1, 1):
            pastetype = Type.TileFast
        elif pastetype == Type.Horz and self.tileimg.size[0] == 1:
            pastetype = Type.HorzFast
        elif pastetype == Type.Vert and self.tileimg.size[1] == 1:
            pastetype = Type.VertFast

        self.pastetype = pastetype

        # Prepare optimisations
        if pastetype == Type.TileFast:
            self.pixel = self.tileimg.getpixel((0, 0))
        elif pastetype == Type.HorzFast:
            self.tileimg = self.tileimg.resize((self.width, self.tileimg.size[1]))
        elif pastetype == Type.VertFast:
            self.tileimg = self.tileimg.resize((self.tileimg.size[0], self.height))

    def expand(self, width, height):
        Type = GridTile.PasteType

        Box.expand(self, width, height)

        if self.pastetype == Type.HorzFast:
            self.tileimg = self.tileimg.resize((self.width, self.tileimg.size[1]))
        elif self.pastetype == Type.VertFast:
            self.tileimg = self.tileimg.resize((self.tileimg.size[0], self.height))

    def draw(self):
        Type = GridTile.PasteType

        if self.pastetype == Type.TileFast:
            self.image.paste_pixel(self.pixel, self.boxcoords)
        elif self.pastetype == Type.Once:
            self.image.paste(self.tileimg, self.offset)
        elif (self.pastetype == Type.Tile or
              self.pastetype == Type.Horz or
              self.pastetype == Type.Vert or
              self.pastetype == Type.HorzFast or
              self.pastetype == Type.VertFast):
            for x in range(self.offset_x, self.offset_x+self.width, self.tileimg.size[0]):
                for y in range(self.offset_y, self.offset_y+self.height, self.tileimg.size[1]):
                    # if self.tileimg.size != (1,1):
                    # print(self.tileimg, self.offset_x, self.offset_x+self.width, self.tileimg.size[0], self.offset_y, self.offset_y+self.height, self.tileimg.size[1])
                    self.image.paste(self.tileimg, (x, y))
        else:
            raise ValueError('Invalid pastetype')

class Sprite(Box):
    # INITIAL_VALUE = FaceState.Happy # Something like this
    def __init__(self, image, skin, init_val=None):
        self.image, self.skin = image, skin

        if init_val is None:
            init_val = self.INITIAL_VALUE
        self.state = init_val # sets self.img, see @state.setter below

        Box.__init__(self, *self.img.size, expandfactor=0)

    @property
    def state(self):
        return self._state
    @state.setter
    def state(self, state):
        self._state = state
        self.img = self.skin[state.name].open()

    def expand(self, width, height):
        if ((width is not None and self.minwidth != width) or
            (height is not None and self.minheight != height)):
            raise NotExpandableError("Sprites can't change size")

    def draw(self):
        self.image.paste(self.img, self.offset)

""" Drawing parts """

class Digit(Sprite):
    INITIAL_VALUE = DigitState.Off

class Face(Sprite):
    INITIAL_VALUE = FaceState.Happy

class Tile(Sprite):
    INITIAL_VALUE = TileState.Unopened

class BorderCorner(GridTile):
    """ Wrapper around Box that draws a corner of a border. """
    def __init__(self, image, skin):
        self.image, self.skin = image, skin

        self.borderimg = skin.open()

        GridTile.__init__(self, image, skin,
            pastetype=GridTile.PasteType.Once,
            expandfactor=0)

    def expand(self, width, height):
        if ((width is not None and self.minwidth != width) or
            (height is not None and self.minheight != height)):
            raise NotExpandableError("Border corners can't change size")

class BorderVEdge(GridTile):
    """ Wrapper around Box that draws a vertical border (l/r). """
    def __init__(self, image, skin):
        self.image, self.skin = image, skin

        GridTile.__init__(self, image, skin,
            pastetype=GridTile.PasteType.Vert,
            expandfactor=0)

    def expand(self, width, height):
        if width is not None and self.minwidth != width:
            raise NotExpandableError("Border vertical edges can't change width")

        GridTile.expand(self, width, height)

class BorderHEdge(GridTile):
    """ Wrapper around Box that draws a horizontal border (t/b). """
    def __init__(self, image, skin):
        self.image, self.skin = image, skin

        GridTile.__init__(self, image, skin,
            pastetype=GridTile.PasteType.Horz,
            expandfactor=1)

    def expand(self, width, height):
        if height is not None and self.minheight != height:
            raise NotExpandableError("Border horizontal edges can't change height")

        GridTile.expand(self, width, height)

class Border(GridBox):
    def __init__(self, image, skin):
        self.image, self.skin = image, skin

        self.tl = tl = BorderCorner(image, skin['tl.png'])
        self.t  = t  = BorderHEdge(image, skin['t.png'])
        self.tr = tr = BorderCorner(image, skin['tr.png'])
        self.l  = l  = BorderVEdge(image, skin['l.png'])
        self.r  = r  = BorderVEdge(image, skin['r.png'])
        self.bl = bl = BorderCorner(image, skin['bl.png'])
        self.b  = b  = BorderHEdge(image, skin['b.png'])
        self.br = br = BorderCorner(image, skin['br.png'])

        m = Box(0, 0)

        self.thickness = Thickness(
                            b=b.height,
                            l=l.width,
                            r=r.width,
                            t=t.height)

        GridBox.__init__(self, [[tl, t, tr], [l, m, r], [bl, b, br]], colfactors=(0, 1, 0), rowfactors=(0, 1, 0))

""" Parts """

class Counter(LayerBox):
    """
    A counter used for the mine counter and the timer
    """
    def __init__(self, image, skin, border=None,
        init_val=0, numdigits=None):
        self.image, self.skin = image, skin

        self.numdigits = numdigits

        if border is None:
            border = Border(image, skin.border)
        self.border = border

        self.digits = digits = [Digit(image, skin.digit) for i in range(numdigits)]

        self.state = init_val

        LayerBox.__init__(self,
            BorderBox(GridBox([digits]), thickness=border.thickness),
            border,
            expandfactor=0)

    @property
    def state(self):
        return self._state
    @state.setter
    def state(self, value):
        if value >= 10**self.numdigits:
            value = 10**self.numdigits-1
        if value <= -10**(self.numdigits-1):
            value = -10**(self.numdigits-1)+1
        self._state = value
        countertext = f'{value:>{self.numdigits}}'

        for i, v in enumerate(countertext):
            if v == ' ':
                self.digits[i].state = DigitState.Off
            elif v == '-':
                self.digits[i].state = DigitState.Minus
            else:
                self.digits[i].state = DigitState.Digit[int(v)]

class Panel(LayerBox):
    """
    The upper half of the minesweeper display, showing the panel.
    """
    def __init__(self, image, skin, bg=None, border=None, lcounter=None, face=None, rcounter=None,
        lcountersize=3, rcountersize=3):
        self.image, self.skin = image, skin

        if bg is None:
            bg = GridTile(image, skin['bg.png'])
        if border is None:
            border = Border(image, skin.border)
        if lcounter is None:
            lcounter = Counter(image, skin.lcounter, numdigits=lcountersize)
        if face is None:
            face = Face(image, skin.face)
        if rcounter is None:
            rcounter = Counter(image, skin.rcounter, numdigits=rcountersize)

        self.bg = bg
        self.border = border
        self.lcounter = lcounter
        self.face = face
        self.rcounter = rcounter

        lcounter.expandfactor = 0
        face.expandfactor = 0
        rcounter.expandfactor = 0

        mainpanel = BorderBox(
            GridBox([[lcounter, Box(0, 0), face, Box(0, 0), rcounter]], rowfactors=(None,), colfactors=(0, 1, 0, 1, 0)),
            thickness=border.thickness)

        LayerBox.__init__(self, bg, mainpanel, border)

class Board(LayerBox):
    """
    The lower half of the minesweeper display, showing the board.
    """
    def __init__(self, image, skin, bg=None, border=None,
        boardcols=30, boardrows=16):
        self.image, self.skin = image, skin

        if bg is None:
            bg = GridTile(image, skin['bg.png'])
        if border is None:
            border = Border(image, skin.border)

        self.bg = bg
        self.border = border

        self.tiles = [  [ Tile(image, skin.tile)
                            for j in range(boardcols)]
                        for i in range(boardrows)]

        tilesbox = GridBox(self.tiles)
        centered_tiles = GridBox([[Box(0, 0), tilesbox, Box(0, 0)]], colfactors=(1, 0, 1))

        mainboard = BorderBox(centered_tiles, thickness=border.thickness)

        LayerBox.__init__(self, bg, mainboard, border)

class Display(LayerBox):
    """
    The whole minesweeper display.

        >>> from PIL import Image

        >>> from .skin import Skin
        >>> from .dirstruct import Multi, Dir

        >>> skindir = 'images_d_tiles'
        >>> skin = Skin(Multi(Dir(skindir), Dir('images')))
        >>> skin.preload_skin()
        >>> displayimg = DisplayImage(None)
        >>> display = Display(displayimg, skin)
        >>> img = Image.new(size=display.size, mode="RGBA")
        >>> displayimg.pil_image = img
        >>> display.draw()
        >>> skin.cache = {} # Clean up for the sake of other tests
    """

    def __init__(self, image, skin, border=None, panel=None, board=None,
        lcountersize=3, rcountersize=3, boardcols=30, boardrows=16):
        self.image, self.skin = image, skin

        if border is None:
            border = Border(image, skin.border)
        if panel is None:
            panel = Panel(image, skin.panel, lcountersize=lcountersize, rcountersize=rcountersize)
        if board is None:
            board = Board(image, skin.board, boardcols=boardcols, boardrows=boardrows)

        self.border = border
        self.panel = panel
        self.board = board

        self.lcounter = panel.lcounter
        self.face = panel.face
        self.rcounter = panel.rcounter
        self.tiles = board.tiles

        panelboard = BorderBox(
            GridBox([[panel], [board]]),
            thickness=border.thickness)

        LayerBox.__init__(self, panelboard, border)
