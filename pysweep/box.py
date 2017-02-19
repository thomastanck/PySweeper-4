from collections import namedtuple
import itertools


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
        self.update_child_offsets()

    @property
    def size(self):
        """ Look like a width/height tuple """
        return (self.width, self.height)
    @property
    def offset(self):
        """ Look like a x/y tuple """
        return (self.offset_x, self.offset_y)
    @property
    def boxcoords(self):
        """ Look like a x1/y1/x2/y2 tuple (for PIL) """
        return (self.offset_x, self.offset_y,
                self.offset_x+self.width, self.offset_y+self.height)
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

    def draw(self):
        pass

class GridBox(Box):
    """
    Makes a grid of boxes.

    subboxes is a list of lists where subboxes[row][col] is a Box.

    Each column and row can be given expandfactors
    to determine how much space is given to each column on expansion.
    By default, all columns and rows will expand and space is allocated evenly

    Each column and row can also be given match options
    that determine if boxes in that column/row will be expanded to fill the space.
    By default, all colmns and rows will try to match their sizes.

    Two boxes with nonzero expandfactors:
        >>> b1 = Box(10, 2)
        >>> b2 = Box(20, 1)
        >>> gb = GridBox([[b1, b2]], colfactors=[1, 3])

        >>> b1.size, b2.size, gb.size, b1.offset, b2.offset, gb.offset
        ((10, 2), (20, 2), (30, 2), (0, 0), (10, 0), (0, 0))

        >>> gb.expand(34, None)

        >>> b1.size, b2.size, gb.size, b1.offset, b2.offset, gb.offset
        ((11, 2), (23, 2), (34, 2), (0, 0), (11, 0), (0, 0))

        >>> gb.expand(33, None)

        >>> b1.size, b2.size, gb.size, b1.offset, b2.offset, gb.offset
        ((10, 2), (23, 2), (33, 2), (0, 0), (10, 0), (0, 0))

        >>> gb.expand(35, None)

        >>> b1.size, b2.size, gb.size, b1.offset, b2.offset, gb.offset
        ((11, 2), (24, 2), (35, 2), (0, 0), (11, 0), (0, 0))


    Two boxes with nonzero expandfactors:
        >>> b1 = Box(2, 10)
        >>> b2 = Box(1, 20)
        >>> gb = GridBox([[b1], [b2]], rowfactors=[1, 3])

        >>> b1.size, b2.size, gb.size, b1.offset, b2.offset, gb.offset
        ((2, 10), (2, 20), (2, 30), (0, 0), (0, 10), (0, 0))

        >>> gb.expand(None, 34)

        >>> b1.size, b2.size, gb.size, b1.offset, b2.offset, gb.offset
        ((2, 11), (2, 23), (2, 34), (0, 0), (0, 11), (0, 0))

        >>> gb.expand(None, 33)

        >>> b1.size, b2.size, gb.size, b1.offset, b2.offset, gb.offset
        ((2, 10), (2, 23), (2, 33), (0, 0), (0, 10), (0, 0))

        >>> gb.expand(None, 35)

        >>> b1.size, b2.size, gb.size, b1.offset, b2.offset, gb.offset
        ((2, 11), (2, 24), (2, 35), (0, 0), (0, 11), (0, 0))
    """
    def __init__(self, subboxes,
            colfactors=None, rowfactors=None):
        self.subboxes = subboxes
        if colfactors is None:
            colfactors = [1] * len(self.cols)
        if rowfactors is None:
            rowfactors = [1] * len(self.rows)
        self.colfactors = [(f if f is not None else 0) for f in colfactors]
        self.rowfactors = [(f if f is not None else 0) for f in rowfactors]

        self.colmatch = [(f is not None) for f in colfactors]
        self.rowmatch = [(f is not None) for f in rowfactors]

        self.colwidths = [max(b.minwidth for b in col) for col in self.cols]
        self.rowheights = [max(b.minheight for b in row) for row in self.rows]

        self.cumcolfactors = list(itertools.accumulate(self.colfactors))
        self.cumrowfactors = list(itertools.accumulate(self.rowfactors))

        self.sumcolfactors = self.cumcolfactors[-1]
        self.sumrowfactors = self.cumrowfactors[-1]

        for colwidth, col, match in zip(self.colwidths, self.cols, self.colmatch):
            if match:
                for b in col:
                    b.expand(colwidth, None)

        for rowheight, row, match in zip(self.rowheights, self.rows, self.rowmatch):
            if match:
                for b in row:
                    b.expand(None, rowheight)

        Box.__init__(self, sum(self.colwidths), sum(self.rowheights))

    @property
    def rows(self):
        return self.subboxes
    @property
    def cols(self):
        return list(zip(*self.subboxes))

    def expand(self, width, height):
        Box.expand(self, width, height)

        if width is not None:
            excesswidth = width - self.minwidth

            if self.sumcolfactors == 0:
                # None of the columns want to expand
                # so we don't expand at all.
                return

            prev_cum_exp = 0

            for col, ef, colwidth in zip(self.cols, self.cumcolfactors, self.colwidths):
                # cumulative expansion
                cum_exp = int(excesswidth * ef / self.sumcolfactors)
                # expansion for this column
                exp = cum_exp - prev_cum_exp
                for b, match in zip(col, self.colmatch):
                    if match:
                        b.expand(colwidth + exp, None)
                prev_cum_exp = cum_exp

        if height is not None:
            excessheight = height - self.minheight

            if self.sumrowfactors == 0:
                # None of the rows want to expand
                # so we don't expand at all.
                return

            prev_cum_exp = 0

            for row, ef, rowheight in zip(self.rows, self.cumrowfactors, self.rowheights):
                # cumulative expansion
                cum_exp = int(excessheight * ef / self.sumrowfactors)
                # expansion for this row
                exp = cum_exp - prev_cum_exp
                for b, match in zip(row, self.rowmatch):
                    if match:
                        b.expand(None, rowheight + exp)
                prev_cum_exp = cum_exp

        self.update_child_offsets()

    def update_child_offsets(self):
        cumcolwidths = [0] + list(itertools.accumulate(b.width for b in self.rows[0]))
        cumrowheights = [0] + list(itertools.accumulate(row[0].height for row in self.rows))
        for row, offset_y in zip(self.rows, cumrowheights):
            for b, offset_x in zip(row, cumcolwidths):
                b.set_parentoffset(self.offset_x + offset_x, self.offset_y + offset_y)

    def draw(self):
        for row in self.rows:
            for b in row:
                b.draw()

class LayerBox(Box):
    def __init__(self, *subboxes, matchsizes=True, expandfactor=1):
        """
        Layers boxes directly on top of each other,
        with the intent of drawing the boxes in order.

            >>> b1 = Box(3, 6)
            >>> b2 = Box(4, 5)
            >>> lb = LayerBox(b1, b2, matchsizes=True)

            >>> b1.size, b2.size, lb.size, b1.offset, b2.offset, lb.offset
            ((4, 6), (4, 6), (4, 6), (0, 0), (0, 0), (0, 0))

            >>> lb.expand(10, 20)

            >>> b1.size, b2.size, lb.size, b1.offset, b2.offset, lb.offset
            ((10, 20), (10, 20), (10, 20), (0, 0), (0, 0), (0, 0))
        """
        self.subboxes = subboxes
        self.matchsizes = matchsizes

        Box.__init__(self, max(b.minwidth for b in subboxes), max(b.minheight for b in subboxes), expandfactor)

        if matchsizes:
            for b in subboxes:
                b.expand(self.minwidth, self.minheight)

    def expand(self, width, height):
        if self.matchsizes:
            for b in self.subboxes:
                b.expand(width, height)

        Box.expand(self, width, height)

    def update_child_offsets(self):
        for b in self.subboxes:
            b.set_parentoffset(self.offset_x, self.offset_y)

    def draw(self):
        for b in self.subboxes:
            b.draw()

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
        innerwidth = width - self.thickness.width if width is not None else None
        innerheight = height - self.thickness.height if height is not None else None

        self.innerbox.expand(innerwidth, innerheight)

        Box.expand(self, width, height)

    def update_child_offsets(self):
        self.innerbox.set_parentoffset(self.offset_x + self.thickness.l, self.offset_y + self.thickness.t)

    def draw(self):
        self.innerbox.draw()

if __name__ == "__main__": # pragma: no cover
    import doctest
    doctest.testmod(optionflags=(doctest.ELLIPSIS | doctest.IGNORE_EXCEPTION_DETAIL))
