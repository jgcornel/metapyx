# TODO: Cleanup Text.__init__
# TODO: Add more custom exceptions
#
from collections import OrderedDict
from math import pi, cos, sin
from enum import Enum
import pyx

class Align(Enum):
    left    =   1
    right   =   2
    center  =   3
    bottom  =   4
    middle  =   5
    top     =   6


class Point:

    __slots__ = ['x', 'y']

    def __init__(self, x, y):

        self.x = x
        self.y = y

    def __getitem__(self, i):

        if i < 0 or i > 1:
            raise IndexError("Point index out of range")

        return self.y if i else self.x

    def __eq__(self, other):

        return self.x == other.x and self.y == other.y

    def __str__(self):

        return '({:3f}, {:3f})'.format(self.x, self.y)

    def __mul__(self, scalar):

        return Point(scalar*self.x, scalar*self.y)

    def __add__(self, other):

        if isinstance(other, self.__class__):
            return Point(self.x + other.x, self.y + other.y)
        elif isinstance(other, tuple):
            return Point(self.x + other[0], self.y + other[1])

    def __sub__(self, other):

        if isinstance(other, self.__class__):
            return Point(self.x - other.x, self.y - other.y)
        elif isinstance(other, tuple):
            return Point(self.x - other[0], self.y - other[1])

    def draw(self, canvas):

        p = pyx.path.circle(self.x, self.y, 0.04)
        canvas.stroke(p, [pyx.deco.filled([pyx.color.rgb.red])])


class Box:

    def __init__(self, debug=False):

        self.debug = debug
        self.parent = None
        self.points = [Point(0,0)]
        self.children = []
        self.decoration = []

    def __min_x(self):
        return min(p.x for p in self.points)

    def __max_x(self):
        return max(p.x for p in self.points)

    def __half_x(self):
        return 0.5 * (self.__max_x() + self.__min_x())

    def __half_y(self):
        return 0.5 * (self.__max_y() + self.__min_y())

    def __min_y(self):
        return min(p.y for p in self.points)

    def __max_y(self):
        return max(p.y for p in self.points)

    @property
    def origin(self):
        return self.points[0]

    @origin.setter
    def origin(self, new_origin):
        dx, dy = new_origin - self.points[0]
        self.translate(dx, dy)

    @property
    def width(self):
        return self.__max_x() - self.__min_x()

    @property
    def height(self):
        return self.__max_y() - self.__min_y()

    @property
    def c(self):
        return Point(self.__half_x(), self.__half_y())

    @property
    def n(self):
        return Point(self.__half_x(), self.__max_y())

    @property
    def ne(self):
        return Point(self.__max_x(), self.__max_y())

    @property
    def e(self):
        return Point(self.__max_x(), self.__half_y())

    @property
    def se(self):
        return Point(self.__max_x(), self.__min_y())

    @property
    def s(self):
        return Point(self.__half_x(), self.__min_y())

    @property
    def sw(self):
        return Point(self.__min_x(), self.__min_y())

    @property
    def w(self):
        return Point(self.__min_x(), self.__half_y())

    @property
    def nw(self):
        return Point(self.__min_x(), self.__max_y())

    @c.setter
    def c(self, c):
        dx, dy = c - self.c
        self.translate(dx, dy)

    @n.setter
    def n(self, n):
        dx, dy = n - self.n
        self.translate(dx, dy)

    @ne.setter
    def ne(self, ne):
        dx, dy = ne - self.ne
        self.translate(dx, dy)

    @e.setter
    def e(self, e):
        dx, dy = e - self.e
        self.translate(dx, dy)

    @se.setter
    def se(self, se):
        dx, dy = se - self.se
        self.translate(dx, dy)

    @s.setter
    def s(self, s):
        dx, dy = s - self.s
        self.translate(dx, dy)

    @sw.setter
    def sw(self, sw):
        dx, dy = sw - self.sw
        self.translate(dx, dy)

    @w.setter
    def w(self, w):
        dx, dy = w - self.w
        self.translate(dx, dy)

    @nw.setter
    def nw(self, nw):
        dx, dy = nw - self.nw
        self.translate(dx, dy)

    def decorate(self, element):
        self.decoration.append(element)

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def draw(self, canvas):

        self._draw(canvas)
        for child in self.children:
            child.draw(canvas)

    def scale(self, factor):

        for child in self.children:
            child.scale(factor)

        for p in self.points:
            p.x *= factor
            p.y *= factor

    def rotate(self, degrees):

        for child in self.children:
            child.rotate(degrees)

        radians = degrees * pi / 180
        cos_a = cos(radians)
        sin_a = sin(radians)

        for p in self.points:
            x, y = p.x, p.y
            p.x = x*cos_a - y*sin_a 
            p.y = x*sin_a + y*cos_a

    def translate(self, dx, dy):

        for child in self.children:
            child.translate(dx, dy)

        for p in self.points:
            p.x += dx
            p.y += dy

    def flip(self, direct):

        raise NotImplementedError("MetaPyx: Box.flip")

    def _draw(self, canvas):

        if self.debug:
            p = pyx.path.rect(0, 0, 1, 1)
            priv_decoration = []
            w, h = self.width, self.height
            x, y = self.__min_x(), self.__min_y()
            priv_decoration.append(pyx.trafo.scale(sx=w, sy=h))
            priv_decoration.append(pyx.trafo.translate(x, y))
            priv_decoration.append(pyx.style.linestyle.dashed)
            canvas.stroke(p, priv_decoration)
            self.points[0].draw(canvas)

        """ Derived classes must specify the remainder """

class Connection(Box):

    def __init__(self, *points):

        super().__init__()
        self.points = points

    def _draw(self, canvas):

        start = self.points[0]
        params = [pyx.path.moveto(start.x, start.y)]
        
        for point in self.points[1:]:
            params.append(pyx.path.lineto(point.x, point.y))

        canvas.stroke(pyx.path.path(*params), self.decoration)

class Rectangle(Box):

    def __init__(self, width=1, height=1, **kwargs):

        super().__init__(**kwargs)
        self.points.append(Point(0, height))
        self.points.append(Point(width, height))
        self.points.append(Point(width, 0))

    def _get_boundaries(self):

        min_x = min(c.origin.x for c in self.children)
        max_x = max(c.e.x for c in self.children)
        min_y = min(c.origin.y for c in self.children)
        max_y = max(c.n.y for c in self.children)

        return min_x, max_x, min_y, max_y

    def horizontal_stretch(self, delta=0):

        if not self.children:
            return

        min_x, max_x, min_y, max_y = self._get_boundaries()

        self.points[0] = Point(min_x-delta, self.points[0].y)
        self.points[1] = Point(min_x-delta, self.points[1].y) 
        self.points[2] = Point(max_x+delta, self.points[2].y)
        self.points[3] = Point(max_x+delta, self.points[3].y)

    def vertical_stretch(self, delta=0):

        if not self.children:
            return

        min_x, max_x, min_y, max_y = self._get_boundaries()

        self.points[0] = Point(self.points[0].x, min_y-delta)
        self.points[1] = Point(self.points[1].x, max_y+delta)
        self.points[2] = Point(self.points[2].x, max_y+delta)
        self.points[3] = Point(self.points[3].x, min_y-delta)        


    def stretch(self, delta=0):

        if not self.children:
            return

        min_x, max_x, min_y, max_y = self._get_boundaries()

        self.points[0] = Point(min_x-delta, min_y-delta)
        self.points[1] = Point(min_x-delta, max_y+delta)
        self.points[2] = Point(max_x+delta, max_y+delta)
        self.points[3] = Point(max_x+delta, min_y-delta)        

    def _draw(self, canvas):

        super()._draw(canvas)

        x, y = self.points[0].x, self.points[0].y
        p = pyx.path.path(pyx.path.moveto(x, y))
        for point in self.points[1:]:
            p.append(pyx.path.lineto(point.x, point.y))
        p.append(pyx.path.lineto(x, y))

        canvas.stroke(p, self.decoration)


class Triangle(Box):

    def __init__(self, width=1, height=1, **kwargs):

        super().__init__(**kwargs)
        self.points.append(Point(width/2, height))
        self.points.append(Point(width, 0))

    def _draw(self, canvas):

        super()._draw(canvas)

        x, y = self.points[0].x, self.points[0].y
        p = pyx.path.path(pyx.path.moveto(x, y))
        for point in self.points[1:]:
            point.draw(canvas)
            p.append(pyx.path.lineto(point.x, point.y))
        p.append(pyx.path.lineto(x, y))

        canvas.stroke(p, self.decoration)


class Circle(Box):

    def __init__(self, radius=0.5, **kwargs):

        super().__init__(**kwargs)
        self.radius = radius
        diameter = 2*radius
        self.points.append(Point(0, diameter))
        self.points.append(Point(diameter, diameter))
        self.points.append(Point(diameter, 0))

    def rotate(self, degrees):

        return

    def _draw(self, canvas):

        super()._draw(canvas)

        p = pyx.path.circle(0, 0, 0.5)
        x1, y1 = self.origin + (self.width/2, self.height/2)
        self.decoration.append(pyx.trafo.scale(sx=self.width, sy=self.height))
        self.decoration.append(pyx.trafo.translate(x1, y1))
        canvas.stroke(p, self.decoration)


class Text(Rectangle):

    Size_ratios = OrderedDict([
        (pyx.text.size.Huge,         2.488),
        (pyx.text.size.huge,         2.074),
        (pyx.text.size.LARGE,        1.728),
        (pyx.text.size.Large,        1.440),
        (pyx.text.size.large,        1.200),
        (pyx.text.size.normalsize,   1.000),
        (pyx.text.size.small,        0.900),
        (pyx.text.size.footnotesize, 0.800),
        (pyx.text.size.scriptsize,   0.700),
        (pyx.text.size.tiny,         0.500),
        ])

    class ScalingError(RuntimeError):

        pass

    class String(Box):

        def __init__(self, py_string, size=pyx.text.size.normal, **kwargs):

            super().__init__(**kwargs)
            self.py_string = py_string
            self.decoration.append(size)
            self.decoration.append(pyx.text.valign.baseline)
            self.initialize()

        def initialize(self):

            t = pyx.text.text(0, 0, self.py_string, self.decoration)
            bb = t.bbox()

            min_x, min_y = 0, 0
            max_x, max_y = 100*bb.width().t, 100*bb.height().t

            self.points.append(Point(min_x, max_y))
            self.points.append(Point(max_x, max_y))
            self.points.append(Point(max_x, min_y))

        def flip(self, direct):

            raise NotImplementedError("MetaPyx: String.flip")

        def _draw(self, canvas):

            super()._draw(canvas)

            has_size = False
            for d in self.decoration:
                if isinstance(d, pyx.text.size):
                    has_size = True
                    break
            if not has_size:
                self.decorate(pyx.text.size.normalsize)

            x1, y1 = self.points[0]
            x2, y2 = self.points[3]
            p = pyx.path.path(pyx.path.moveto(x1, y1), pyx.path.lineto(x2, y2))
            canvas.draw(p, [pyx.deco.curvedtext(self.py_string,
                                                textattrs=self.decoration)])

    def __init__(self,
                 *py_strings,
                 size=pyx.text.size.normal,
                 alignment=Align.center,
                 **kwargs):

        assert py_strings, "MetaPyx: Empty Text"

        super().__init__(**kwargs)
        self.py_strings = py_strings
        self.alignment = alignment
        self.size = size

        self.longest_ = None

        self.dict_ = {}

        self.initialize()
        self.find_longest()
        self.stretch(0.1)

    def decorate(self):

        raise NotImplementedError("MetaPyx: Text.decorate")

    def scale(self, factor):

        if factor == 1:
            return

        new_height = factor * self.height
        new_width  = factor * self.width


        my_ratio = 0
        my_ratio = Text.Size_ratios[self.size]

        for size, ratio in Text.Size_ratios.items():

            if factor < ratio/my_ratio:
                continue 

            longest_width = Text.String(self.longest_, size=size).width
            if new_width < longest_width:
                continue

            """ break if you find a size that fits the requirements """
            break

        else:
            """ the loop terminated normally """

            raise Text.ScalingError("MetaPyx: Text.scale cannot fit the text")

        super().scale(factor)

        self.size = size
        for string in self.children:
            string.decoration = []
            string.decoration.append(size)
            string.decoration.append(pyx.text.valign.baseline)        

    def initialize(self):

        golden = 1.618034

        for py_string in self.py_strings:
            string = Text.String(py_string, size=self.size, debug=False)
            self.dict_[py_string] = string
            self.add_child(string)

        height = max(child.height for child in self.children)
        self.delta = 0.66*(golden - 1) * height

        for kid in self.children:
            kid.nw = self.nw + (self.delta, -self.delta)

        top_to_bottom(*self.children, alignment=self.alignment, delta=self.delta)

    def find_longest(self):

        max_length = 0
        for py_string, string in self.dict_.items():
            length = string.width
            if length > max_length:
                max_length = length
                self.longest_ = py_string

    def __getitem__(self, key):
        return self.dict_[key]

    def _draw(self, canvas):

        """ do not draw the rectangle """
        pass


def left_to_right(anchor_box, *boxes, alignment=Align.middle, delta=1):

    if not boxes:
        return

    box = boxes[0]

    if alignment is Align.bottom:
        box.sw = anchor_box.se + (delta, 0)
    elif alignment is Align.middle:
        box.w  = anchor_box.e  + (delta, 0)
    elif alignment is Align.top:
        box.nw = anchor_box.ne + (delta, 0)
    else:
        raise(RuntimeError('Invalid Align: {}'.format(alignment)))

    left_to_right(boxes[0], *boxes[1:], alignment=alignment, delta=delta)


def right_to_left(anchor_box, *boxes, alignment=Align.middle, delta=1):

    if not boxes:
        return

    box = boxes[0]

    if alignment is Align.bottom:
        box.se = anchor_box.sw - (delta, 0)
    elif alignment is Align.middle:
        box.e  = anchor_box.w  - (delta, 0)
    elif alignment is Align.top:
        box.ne = anchor_box.nw - (delta, 0)
    else:
        raise(RuntimeError('Invalid Align: {}'.format(alignment)))

    right_to_left(boxes[0], *boxes[1:], alignment=alignment, delta=delta)


def bottom_to_top(anchor_box, *boxes, alignment=Align.center, delta=1):

    if not boxes:
        return

    box = boxes[0]

    if alignment is Align.left:
        box.sw = anchor_box.nw + (0, delta)
    elif alignment is Align.center:
        box.s  = anchor_box.n  + (0, delta)
    elif alignment is Align.right:
        box.se = anchor_box.ne + (0, delta)
    else:
        raise(RuntimeError('Invalid Align: {}'.format(alignment)))

    bottom_to_top(boxes[0], *boxes[1:], alignment=alignment, delta=delta)


def top_to_bottom(anchor_box, *boxes, alignment=Align.center, delta=1):

    if not boxes:
        return

    box = boxes[0]

    if alignment is Align.left:
        box.nw = anchor_box.sw - (0, delta)
    elif alignment is Align.center:
        box.n  = anchor_box.s  - (0, delta)
    elif alignment is Align.right:
        box.ne = anchor_box.se - (0, delta)
    else:
        raise(RuntimeError('Invalid Align: {}'.format(alignment)))

    top_to_bottom(boxes[0], *boxes[1:], alignment=alignment, delta=delta)


def partition_segment(start, stop, fraction):

    point = Point(0, 0)

    point.x = start.x + fraction * (stop.x - start.x)
    point.y = start.y + fraction * (stop.y - start.y)

    return point
