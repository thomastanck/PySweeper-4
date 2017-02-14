from enum import Enum
from collections import namedtuple


class Alignment(Enum):
    # BOTTOMLEFT = 0
    BOTTOM = 1
    # BOTTOMRIGHT = 2
    LEFT = 3
    # MIDDLE = 4
    RIGHT = 5
    # TOPLEFT = 6
    TOP = 7
    # TOPRIGHT = 8

class Part:
    """Base class for all parts of a display.

    Similar to tkinter widgets,
    except these parts will eventually paste their contents onto a PIL image.
    """
    pass

Connection = namedtuple('Connection', ['myalignment', 'otherpart', 'otheralignment'])

class Thickness:
    """
    Stores the thickness of a set of borders.
    """
    def __init__(self, b=0, l=0, r=0, t=0):
        self.b = b
        self.l = l
        self.r = r
        self.t = t
    @property
    def size(self):
        return (self.width, self.height)
    @property
    def width(self):
        return self.l + self.r
    @property
    def height(self):
        return self.b + self.t


class Box:
    """
    Represents a rectangular size and position.

    Will be used to position/reason about the minesweeper UI.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.offset = (0, 0)

    @property
    def size(self):
        """ Look like a width/height tuple """
        return (self.width, self.height)
    @size.setter
    def size(self, newsize):
        self.width, self.height = newsize

    def expand(self, width, height):
        assert ( (width > self.width if width else True) and
                 (width > self.height if height else True) )
        if width:
            self.width = width
        if height:
            self.height = height

class HSplitBox(Box):
    def __init__(self, top, bottom, expand=True):
        """
        Makes a box around two sub boxes, arranging them vertically.

        If `expand` is True,
        it will try to match the widths of the two subboxes by calling `.expand` on the narrower box.
        """
        super(HSplitBox, self).__init__()

        self.top = top
        self.bottom = bottom

        if expand:
            if top.width > bottom.width:
                bottom.expand(top.width, None)
            else:
                top.expand(bottom.width, None)

class VSplitBox(Box):
    def __init__(self, left, right, expand=True):
        """
        Makes a box around two sub boxes, arranging them horizontally.

        If `expand` is True,
        it will try to match the heights of the two subboxes by calling `.expand` on the shorter box.
        """
        super(VSplitBox, self).__init__()

        self.left = left
        self.right = right

        if expand:
            if left.height > right.height:
                right.expand(None, left.height)
            else:
                left.expand(None, right.height)

class BorderBox(Box):
    def __init__(self, innerbox, thickness=None):
        super(BorderBox, self).__init__()
        self.innerbox = innerbox
        if thickness:
            self.thickness = thickness
        else:
            self.thickness = thickness = Thickness()
        self.size = (innerbox.width + thickness.width), (innerbox.height + thickness.height)
    @property
    def offset(self):
        return (self.thickness.l, self.thickness.t)

class RectPart(Part):
    """
    Rectangular part
    """
    def __init__(self):
        super(RectPart, self).__init__()
        self._connection = None
    def connect(self, myalignment, otherpart, otheralignment):
        self._connection = Connection(myalignment, otherpart, otheralignment)

class BorderPart(Part):
    """
    Represents a border around some parts
    """
    def __init__(self, images):
        self._images = images
        self._contains = []

    def contains(self, part):
        self._contains.append(part)

class RectPart(Part):
    """
    Represents a normal part that doesn't have more parts inside it...
    """
    def __init__(self):
        pass
