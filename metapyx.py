import math
from enum import Enum
from pyx import *

class Align(Enum):
    left    =   1
    right   =   2
    center  =   3
    bottom  =   4
    middle  =   5
    top     =   6

class Direct(Enum):

    """ subsequent computations depend on this order and these values """
    up      =   0
    right   =   1
    down    =   2
    left    =   3

class Point:

    __slots__ = ['x', 'y']

    def __init__(self, x, y):

        self.x = x
        self.y = y

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

        p = path.circle(self.x, self.y, 0.1)
        canvas.stroke(p, [deco.filled([color.rgb.black])])

class Box:

    def __init__(self, width=1, height=1):

        self.__origin = Point(0,0)
        self.width = width
        self.height = height
        self.parent = None
        self.styles = []
        self.children = []

    @property
    def origin(self):
        return self.__origin

    @origin.setter
    def origin(self, new_origin):
        self.__origin = new_origin

    @property
    def aspect(self):
        return self.styles

    @aspect.setter
    def aspect(self, value):
        self.styles.append(value)

    @property
    def c(self):
        return self.origin + (self.width/2, self.height/2)

    @property
    def n(self):
        return self.origin + (self.width/2, self.height)

    @property
    def ne(self):
        return self.origin + (self.width, self.height)

    @property
    def e(self):
        return self.origin + (self.width, self.height/2)

    @property
    def se(self):
        return self.origin + (self.width, 0)

    @property
    def s(self):
        return self.origin + (self.width/2, 0)

    @property
    def sw(self):
        return self.origin

    @property
    def w(self):
        return self.origin + (0, self.height/2)

    @property
    def nw(self):
        return self.origin + (0, self.height)

    @c.setter
    def c(self, c):
        self.origin = c - (self.width/2, self.height/2)

    @n.setter
    def n(self, n):
        self.origin = n - (self.width/2, self.height)

    @ne.setter
    def ne(self, ne):
        self.origin = ne - (self.width, self.height)

    @e.setter
    def e(self, e):
        self.origin = e - (self.width, self.height/2)

    @se.setter
    def se(self, se):
        self.origin = se - (self.width, 0)

    @s.setter
    def s(self, s):
        self.origin = s - (self.width/2, 0)

    @sw.setter
    def sw(self, sw):
        self.origin = sw

    @w.setter
    def w(self, w):
        self.origin = w - (0, self.height/2)

    @nw.setter
    def nw(self, nw):
        self.origin = nw - (0, self.height)

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def draw(self, canvas, level=0):

        self._draw(canvas, level)
        for child in self.children:
            child.draw(canvas, level+1)

    def stretch(self, delta=1):

        if not self.children:
            return

        min_x = min(map(lambda c: c.origin.x, self.children))
        min_y = min(map(lambda c: c.origin.y, self.children))
        max_x = max(map(lambda c: c.e.x, self.children))
        max_y = max(map(lambda c: c.n.y, self.children))

        self.width  = (max_x + delta) - (min_x - delta)
        self.height = (max_y + delta) - (min_y - delta)

        delta_x = delta - min_x
        delta_y = delta - min_y

        for child in self.children:
            child.origin = child.origin + (delta_x, delta_y)

    def tilt_right(self):

        for child in self.children:
            child.tilt_right()

        if self.parent:
            x, y = self.origin.x, self.origin.y
            W = self.parent.width
            w = self.width
            self.origin.x, self.origin.y = y, W - (x + w)

        self.width, self.height = self.height, self.width

    def tilt_left(self):

        for child in self.children:
            child.tilt_left()

        if self.parent:
            x, y = self.origin.x, self.origin.y
            H = self.parent.height
            h = self.height
            self.origin.x, self.origin.y = H - (y + h), x

        self.width, self.height = self.height, self.width

    def tilt_down(self):

        self.tilt_right()
        self.tilt_right()

    def flip_horizontal(self):

        for child in self.children:
            child.flip_horizontal()

        if self.parent:
            x, y = self.origin.x, self.origin.y
            W = self.parent.width
            w = self.width
            self.origin.x, self.origin.y = W - (x + w), y

    def flip_vertical(self):

        for child in self.children:
            child.flip_vertical()

        if self.parent:
            x, y = self.origin.x, self.origin.y
            H = self.parent.height
            h = self.height
            self.origin.x, self.origin.y = x, H - (y + h)        

    def get(self, location, level=0):

        """ An AttributeError may be raised """
        relative_location = self.__getattribute__(location)

        if level < 0:
            return Point(0, 0)
        elif level == 0:
            return relative_location
        else:
            parent_origin = self.parent.get('origin', level-1)
            return parent_origin + relative_location

    def _draw(self, canvas, level=0):

        """ placeholder only """
        pass

class Rectangle(Box):

    def _draw(self, canvas, level=0):

        p = path.rect(0, 0, 1, 1)
        sw = self.get('sw', level)
        self.styles.append(trafo.scale(sx=self.width, sy=self.height))
        self.styles.append(trafo.translate(sw.x, sw.y))
        canvas.stroke(p, self.styles)

class Ellipse(Box):

    def _draw(self, canvas, level=0):

        if not self.border:
            return

        sw = self.get('sw', level)
        p = path.circle(0, 0, 0.5) # radius is required
        self.styles.append(trafo.scale(sx=self.width, sy=self.height))
        self.styles.append(trafo.translate(sw.x + self.width/2,
                                           sw.y + self.height/2))
        canvas.stroke(p, self.styles)

class String(Box):

    def __init__(self, py_string, direction=Direct.right):

        super().__init__()
        self.py_string = py_string
        self.direction = direction
        self.initialize()

    def initialize(self):

        t = text.text(0, 0, self.py_string, self.styles)
        bb = t.bbox()

        if self.direction == Direct.left or\
           self.direction == Direct.right:

               self.width = 100*bb.width().t
               self.height = 100*bb.height().t

        elif self.direction == Direct.up or\
             self.direction == Direct.down:

               self.height = 100*bb.width().t
               self.width  = 100*bb.height().t

    @property
    def aspect(self):
        return self.styles

    @aspect.setter
    def aspect(self, value):
        self.styles.append(value)
        self.initialize()

    def tilt_right(self):

        super().tilt_right()

        i = self.direction.value
        self.direction = Direct((i+1)%4)

    def tilt_left(self):

        super().tilt_left()

        i = self.direction.value
        self.direction = Direct((i+3)%4)

    def tilt_down(self):

        super().tilt_down()

        i = self.direction.value
        self.direction = Direct((i+2)%4)

    def flip_horizontal(self):

        raise NotImplementedError("MetaPyx: String.flip_horizontal")

    def flip_vertical(self):

        raise NotImplementedError("MetaPyx: String.flip_vertical")

    def _draw(self, canvas, level=0):

        if self.direction == Direct.up:
            """ from se to ne """
            se = self.get('se', level)
            ne = self.get('ne', level)
            p = path.path(path.moveto(se.x, se.y), path.lineto(ne.x, ne.y))
            canvas.draw(p, [deco.curvedtext(self.py_string, textattrs=self.styles)])

        elif self.direction == Direct.down:
            """ from nw to sw """
            nw = self.get('nw', level)
            sw = self.get('sw', level)
            p = path.path(path.moveto(nw.x, nw.y), path.lineto(sw.x, sw.y))
            canvas.draw(p, [deco.curvedtext(self.py_string, textattrs=self.styles)])

        elif self.direction == Direct.left:
            """ from ne to nw """
            ne = self.get('ne', level)
            nw = self.get('nw', level)
            p = path.path(path.moveto(ne.x, ne.y), path.lineto(nw.x, nw.y))
            canvas.draw(p, [deco.curvedtext(self.py_string, textattrs=self.styles)])

        elif self.direction == Direct.right:
            """ from sw to se """
            sw = self.get('sw', level)
            se = self.get('se', level)
            p = path.path(path.moveto(sw.x, sw.y), path.lineto(se.x, se.y))
            canvas.draw(p, [deco.curvedtext(self.py_string, textattrs=self.styles)])

class Line(Box):

    def __init__(self, points=[]):

        super().__init__()

        self.points = points if points else []
        self.parent = None

    def xs(self):

        return [p.x for p in self.points]

    def ys(self):

        return [p.y for p in self.points]

    @property
    def origin(self):
        return Point(min(self.xs()), min(self.ys()))

    @origin.setter
    def origin(self, new_origin):

        delta_x = self.origin.x - new_origin.x
        delta_y = self.origin.y - new_origin.y
        for point in self.points:
            point.x -= delta_x
            point.y -= delta_y
    @property
    def w(self):
        return Point(min(self.xs()), (min(self.ys()) + max(self.ys()))/2)

    @property
    def e(self):
        return Point(max(self.xs()), (min(self.ys()) + max(self.ys()))/2)

    @property
    def n(self):
        return Point((min(self.xs()) + max(self.xs()))/2, max(self.ys()))

    @property
    def s(self):
        return Point((min(self.xs()) + max(self.xs()))/2, min(self.ys()))

    def draw(self, canvas, level=0):

        p0 = self.points[0]
        if self.parent:
            p0 += self.parent.get('sw', level-1)

        params = [path.moveto(p0.x, p0.y)]

        for point in self.points[1:]:
            pi = point
            if self.parent:
                pi += self.parent.get('sw', level-1)
            params.append(path.lineto(pi.x, pi.y))

        p = path.path(*params)
        canvas.stroke(p, self.styles)

def left_to_right(alignment, delta, anchor_box, *boxes):

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

    left_to_right(alignment, delta, boxes[0], *(boxes[1:]))

def right_to_left(alignment, delta, anchor_box, *boxes):

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

    right_to_left(alignment, delta, boxes[0], *(boxes[1:]))

def bottom_to_top(alignment, delta, anchor_box, *boxes):

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

    bottom_to_top(alignment, delta, boxes[0], *(boxes[1:]))


def top_to_bottom(alignment, delta, anchor_box, *boxes):

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

    top_to_bottom(alignment, delta, boxes[0], *(boxes[1:]))

def partition_segment(start, stop, fraction):

    point = Point(0, 0)

    point.x = start.x + fraction * (stop.x - start.x)
    point.y = start.y + fraction * (stop.y - start.y)

    return point



class Text(Box):

    """ A Text object is a collection of strings """

    def __init__(self,
                 strings=[],
                 border=None,
                 alignment=Align.center):

        super().__init__(border)
        self.strings = strings if strings else []
        self.alignment = alignment

        self.dict_ = {}

        self.initialize()

    def initialize(self):

        golden = (1 + 5**0.5) / 2

        for line in self.strings:
            self.dict_[line.string] = line
            self.add_child(line)

        height = max(child.height for child in self.children)
        delta  = 0.66*(golden - 1) * height

        top_to_bottom(self.alignment, delta, self.children[0],
                *self.children[1:])

        self.stretch(delta)

    def __getitem__(self, key):
        return self.dict_[key]
