from enum import Enum
from collections import namedtuple


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

class TooSmallError(ValueError):
    """
    Raised when trying to resize a box to less than its minimum size
    """
    pass

class Box:
    """
    Represents a rectangular size and position.

    Will be used to position/reason about the minesweeper UI.

        >>> b = Box(10, 10)
        >>> b.size
        (10, 10)
        >>> b.expand(16, None)
        >>> b.size
        (16, 10)
        >>> b.expand(None, 20)
        >>> b.size
        (16, 20)
        >>> b.expand(32, 64)
        >>> b.size
        (32, 64)
        >>> b.expand(10, None)
        >>> b.size
        (10, 64)
        >>> b.expand(None, 10)
        >>> b.size
        (10, 10)
        >>> b.expand(10, 10)
        >>> b.size
        (10, 10)
        >>> b.expand(10, 9)
        Traceback (most recent call last):
          ...
        TooSmallError: Tried to resize box to less than its minimum size

        >>> b = Box(10, 10)
        >>> b.offset
        (0, 0)
        >>> b.set_parentoffset(3, 5)
        >>> b.offset
        (3, 5)
        >>> b.set_localoffset(30, 50)
        >>> b.offset
        (33, 55)
        >>> b.set_parentoffset(None, 8)
        >>> b.offset
        (33, 58)
        >>> b.set_parentoffset(5, None)
        >>> b.offset
        (35, 58)
        >>> b.set_localoffset(None, 100)
        >>> b.offset
        (35, 108)
        >>> b.set_localoffset(80, None)
        >>> b.offset
        (85, 108)
    """
    def __init__(self, minwidth, minheight, expandfactor=1):
        self.width = self.minwidth = minwidth
        self.height = self.minheight = minheight
        self.expandfactor = expandfactor
        self.localoffset_x = 0
        self.localoffset_y = 0
        self.parentoffset_x = 0
        self.parentoffset_y = 0
        self.set_localoffset(0, 0)
        self.set_parentoffset(0, 0)

    @property
    def size(self):
        """ Look like a width/height tuple """
        return (self.width, self.height)
    @property
    def offset(self):
        """ Look like a x/y tuple """
        return (self.offset_x, self.offset_y)
    @property
    def offset_x(self):
        """ Sum of local and parent x offsets """
        return self.localoffset_x + self.parentoffset_x
    @property
    def offset_y(self):
        """ Sum of local and parent y offsets """
        return self.localoffset_y + self.parentoffset_y

    def expand(self, width, height):
        if not ( (width >= self.minwidth if width else True) and
                 (height >= self.minheight if height else True) ):
            raise TooSmallError('Tried to resize box to less than its minimum size')
        if width:
            self.width = width
        if height:
            self.height = height

    def set_localoffset(self, x, y):
        if x is not None:
            self.localoffset_x = x
        if y is not None:
            self.localoffset_y = y
        self.update_child_offsets()

    def set_parentoffset(self, x, y):
        if x is not None:
            self.parentoffset_x = x
        if y is not None:
            self.parentoffset_y = y
        self.update_child_offsets()

    def update_child_offsets(self):
        pass

class HSplitBox(Box):
    def __init__(self, top, bottom, matchwidths=True, expandfactor=1):
        """
        Makes a box around two sub boxes, arranging them vertically.

        If `matchwidths` is True,
        it will try to match the widths of the two subboxes by calling `.expand` on the narrower box.

        Two boxes with nonzero expandfactors:
            >>> b1 = Box(2, 10)
            >>> b2 = Box(1, 20, expandfactor=3)
            >>> hsb = HSplitBox(b1, b2, matchwidths=True)

            >>> b1.size, b2.size, hsb.size, b1.offset, b2.offset, hsb.offset
            ((2, 10), (2, 20), (2, 30), (0, 0), (0, 10), (0, 0))

            >>> hsb.expand(None, 34)

            >>> b1.size, b2.size, hsb.size, b1.offset, b2.offset, hsb.offset
            ((2, 11), (2, 23), (2, 34), (0, 0), (0, 11), (0, 0))

            >>> hsb.expand(None, 33)

            >>> b1.size, b2.size, hsb.size, b1.offset, b2.offset, hsb.offset
            ((2, 10), (2, 23), (2, 33), (0, 0), (0, 10), (0, 0))

            >>> hsb.expand(None, 35)

            >>> b1.size, b2.size, hsb.size, b1.offset, b2.offset, hsb.offset
            ((2, 11), (2, 24), (2, 35), (0, 0), (0, 11), (0, 0))

        One box with zero expandfactor:
            >>> b1 = Box(2, 10)
            >>> b2 = Box(1, 20, expandfactor=0)
            >>> hsb = HSplitBox(b1, b2, matchwidths=True)

            >>> b1.size, b2.size, hsb.size, b1.offset, b2.offset, hsb.offset
            ((2, 10), (2, 20), (2, 30), (0, 0), (0, 10), (0, 0))

            >>> hsb.expand(None, 34)

            >>> b1.size, b2.size, hsb.size, b1.offset, b2.offset, hsb.offset
            ((2, 14), (2, 20), (2, 34), (0, 0), (0, 14), (0, 0))

            >>> hsb.expand(None, 33)

            >>> b1.size, b2.size, hsb.size, b1.offset, b2.offset, hsb.offset
            ((2, 13), (2, 20), (2, 33), (0, 0), (0, 13), (0, 0))

            >>> hsb.expand(None, 35)

            >>> b1.size, b2.size, hsb.size, b1.offset, b2.offset, hsb.offset
            ((2, 15), (2, 20), (2, 35), (0, 0), (0, 15), (0, 0))

        Both boxes with zero expandfactors:
            >>> b1 = Box(2, 10, expandfactor=0)
            >>> b2 = Box(1, 20, expandfactor=0)
            >>> hsb = HSplitBox(b1, b2, matchwidths=True)

            >>> b1.size, b2.size, hsb.size, b1.offset, b2.offset, hsb.offset
            ((2, 10), (2, 20), (2, 30), (0, 0), (0, 10), (0, 0))

            >>> hsb.expand(None, 34)

            >>> b1.size, b2.size, hsb.size, b1.offset, b2.offset, hsb.offset
            ((2, 10), (2, 20), (2, 34), (0, 0), (0, 10), (0, 0))

            >>> hsb.expand(None, 33)

            >>> b1.size, b2.size, hsb.size, b1.offset, b2.offset, hsb.offset
            ((2, 10), (2, 20), (2, 33), (0, 0), (0, 10), (0, 0))

            >>> hsb.expand(None, 35)

            >>> b1.size, b2.size, hsb.size, b1.offset, b2.offset, hsb.offset
            ((2, 10), (2, 20), (2, 35), (0, 0), (0, 10), (0, 0))
        """
        self.top = top
        self.bottom = bottom
        self.matchwidths = matchwidths

        Box.__init__(self, max(top.minwidth, bottom.minwidth), top.minheight + bottom.minheight, expandfactor)

        if matchwidths:
            if top.width >= bottom.width:
                bottom.expand(top.width, None)
            else:
                top.expand(bottom.width, None)

    def expand(self, width, height):
        Box.expand(self, width, height)

        if self.matchwidths:
            self.bottom.expand(self.top.width, None)
            self.top.expand(self.bottom.width, None)

        excessheight = height - self.minheight

        total_ef = self.top.expandfactor + self.bottom.expandfactor

        if total_ef == 0:
            # Neither the top or the bottom want to expand,
            # so we don't expand at all.
            return

        top_expansion = int(excessheight * self.top.expandfactor / total_ef)
        bottom_expansion = excessheight - top_expansion

        top_height = self.top.minheight + top_expansion
        bottom_height = self.bottom.minheight + bottom_expansion

        self.top.expand(None, top_height)
        self.bottom.expand(None, bottom_height)

        self.update_child_offsets()

    def update_child_offsets(self):
        self.top.set_parentoffset(self.offset_x, self.offset_y)
        self.bottom.set_parentoffset(self.offset_x, self.offset_y + self.top.height)

class VSplitBox(Box):
    def __init__(self, left, right, matchheights=True, expandfactor=1):
        """
        Makes a box around two sub boxes, arranging them horizontally.

        If `matchheights` is True,
        it will try to match the heights of the two subboxes by calling `.expand` on the shorter box.

        Two boxes with nonzero expandfactors:
            >>> b1 = Box(10, 2)
            >>> b2 = Box(20, 1, expandfactor=3)
            >>> vsb = VSplitBox(b1, b2, matchheights=True)

            >>> b1.size, b2.size, vsb.size, b1.offset, b2.offset, vsb.offset
            ((10, 2), (20, 2), (30, 2), (0, 0), (10, 0), (0, 0))

            >>> vsb.expand(34, None)

            >>> b1.size, b2.size, vsb.size, b1.offset, b2.offset, vsb.offset
            ((11, 2), (23, 2), (34, 2), (0, 0), (11, 0), (0, 0))

            >>> vsb.expand(33, None)

            >>> b1.size, b2.size, vsb.size, b1.offset, b2.offset, vsb.offset
            ((10, 2), (23, 2), (33, 2), (0, 0), (10, 0), (0, 0))

            >>> vsb.expand(35, None)

            >>> b1.size, b2.size, vsb.size, b1.offset, b2.offset, vsb.offset
            ((11, 2), (24, 2), (35, 2), (0, 0), (11, 0), (0, 0))

        One box with zero expandfactor:
            >>> b1 = Box(10, 2)
            >>> b2 = Box(20, 1, expandfactor=0)
            >>> vsb = VSplitBox(b1, b2, matchheights=True)

            >>> b1.size, b2.size, vsb.size, b1.offset, b2.offset, vsb.offset
            ((10, 2), (20, 2), (30, 2), (0, 0), (10, 0), (0, 0))

            >>> vsb.expand(34, None)

            >>> b1.size, b2.size, vsb.size, b1.offset, b2.offset, vsb.offset
            ((14, 2), (20, 2), (34, 2), (0, 0), (14, 0), (0, 0))

            >>> vsb.expand(33, None)

            >>> b1.size, b2.size, vsb.size, b1.offset, b2.offset, vsb.offset
            ((13, 2), (20, 2), (33, 2), (0, 0), (13, 0), (0, 0))

            >>> vsb.expand(35, None)

            >>> b1.size, b2.size, vsb.size, b1.offset, b2.offset, vsb.offset
            ((15, 2), (20, 2), (35, 2), (0, 0), (15, 0), (0, 0))

        Both boxes with zero expandfactors:
            >>> b1 = Box(10, 2, expandfactor=0)
            >>> b2 = Box(20, 1, expandfactor=0)
            >>> vsb = VSplitBox(b1, b2, matchheights=True)

            >>> b1.size, b2.size, vsb.size, b1.offset, b2.offset, vsb.offset
            ((10, 2), (20, 2), (30, 2), (0, 0), (10, 0), (0, 0))

            >>> vsb.expand(34, None)

            >>> b1.size, b2.size, vsb.size, b1.offset, b2.offset, vsb.offset
            ((10, 2), (20, 2), (34, 2), (0, 0), (10, 0), (0, 0))

            >>> vsb.expand(33, None)

            >>> b1.size, b2.size, vsb.size, b1.offset, b2.offset, vsb.offset
            ((10, 2), (20, 2), (33, 2), (0, 0), (10, 0), (0, 0))

            >>> vsb.expand(35, None)

            >>> b1.size, b2.size, vsb.size, b1.offset, b2.offset, vsb.offset
            ((10, 2), (20, 2), (35, 2), (0, 0), (10, 0), (0, 0))
        """
        self.left = left
        self.right = right
        self.matchheights = matchheights

        Box.__init__(self, left.minwidth + right.minwidth, max(left.minheight, right.minheight), expandfactor)

        if matchheights:
            if left.height >= right.height:
                right.expand(None, left.height)
            else:
                left.expand(None, right.height)

    def expand(self, width, height):
        Box.expand(self, width, height)

        if self.matchheights:
            self.right.expand(None, self.left.height)
            self.left.expand(None, self.right.height)

        excesswidth = width - self.minwidth

        total_ef = self.left.expandfactor + self.right.expandfactor

        if total_ef == 0:
            # Neither the left or the right want to expand,
            # so we don't expand at all.
            return

        left_expansion = int(excesswidth * self.left.expandfactor / total_ef)
        right_expansion = excesswidth - left_expansion

        left_width = self.left.minwidth + left_expansion
        right_width = self.right.minwidth + right_expansion

        self.left.expand(left_width, None)
        self.right.expand(right_width, None)

        self.update_child_offsets()

    def update_child_offsets(self):
        self.left.set_parentoffset(self.offset_x, self.offset_y)
        self.right.set_parentoffset(self.offset_x + self.left.width, self.offset_y)

class LayerBox(Box):
    def __init__(self, front, back, matchsizes=True, expandfactor=1):
        """
        Layers two boxes directly on top of each other,
        drawing the back box first, then drawing the front box.

            >>> b1 = Box(3, 6)
            >>> b2 = Box(4, 5)
            >>> lb = LayerBox(b1, b2, matchsizes=True)

            >>> b1.size, b2.size, lb.size, b1.offset, b2.offset, lb.offset
            ((4, 6), (4, 6), (4, 6), (0, 0), (0, 0), (0, 0))

            >>> lb.expand(10, 20)

            >>> b1.size, b2.size, lb.size, b1.offset, b2.offset, lb.offset
            ((10, 20), (10, 20), (10, 20), (0, 0), (0, 0), (0, 0))
        """
        self.front = front
        self.back = back

        Box.__init__(self, max(front.minwidth, back.minwidth), max(front.minheight, back.minheight), expandfactor)

        self.matchsizes = matchsizes
        if matchsizes:
            if front.height >= back.height:
                back.expand(None, front.height)
            else:
                front.expand(None, back.height)

            if front.width >= back.width:
                back.expand(front.width, None)
            else:
                front.expand(back.width, None)

    def expand(self, width, height):
        if self.matchsizes:
            self.front.expand(width, height)
            self.back.expand(width, height)

        Box.expand(self, width, height)

    def update_child_offsets(self):
        self.front.set_parentoffset(self.offset_x, self.offset_y)
        self.back.set_parentoffset(self.offset_x, self.offset_y)

class BorderBox(Box):
    def __init__(self, innerbox, thickness=None, expandfactor=1):
        """
        A box around another box with a padding around it determined by the thickness.

            >>> b1 = Box(30, 60)
            >>> bb = BorderBox(b1, thickness=Thickness(1, 2, 4, 8))

            >>> b1.size, bb.size, b1.offset, bb.offset
            ((30, 60), (36, 69), (2, 8), (0, 0))

            >>> bb.expand(40, 80)

            >>> b1.size, bb.size, b1.offset, bb.offset
            ((34, 71), (40, 80), (2, 8), (0, 0))
        """
        self.innerbox = innerbox

        if thickness:
            self.thickness = thickness
        else:
            self.thickness = thickness = Thickness()

        Box.__init__(self, innerbox.width + thickness.width, innerbox.height + thickness.height, expandfactor)

    def expand(self, width, height):
        innerwidth = width - self.thickness.width
        innerheight = height - self.thickness.height

        self.innerbox.expand(innerwidth, innerheight)

        Box.expand(self, width, height)

    def update_child_offsets(self):
        self.innerbox.set_parentoffset(self.offset_x + self.thickness.l, self.offset_y + self.thickness.t)

if __name__ == "__main__":
    import doctest
    doctest.testmod(optionflags=(doctest.ELLIPSIS | doctest.IGNORE_EXCEPTION_DETAIL))
