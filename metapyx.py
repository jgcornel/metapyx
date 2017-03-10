import math
from pyx import *

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

    def __init__(self, width=1, height=1, border=True):

        self.__origin = Point(0,0)
        self.width = width
        self.height = height
        self.border = border
        self.parent = None
        self.style = []
        self.children = []
        self.connections = []

    @property
    def origin(self):
        return self.__origin

    @origin.setter
    def origin(self, new_origin):
        self.__origin = new_origin

    def add_child(self, child):

        self.children.append(child)
        child.parent = self

    def add_style(self, style_element):

        self.style.append(style_element)

    def draw(self, canvas, level=0):

        self._draw(canvas, level)
        for child in self.children:
            child.draw(canvas, level+1)
        for connection in self.connections:
            connection.draw(canvas, level+1)

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

    def resize(self, width, height):

        delta_x = (width - self.width)/2
        delta_y = (height - self.height)/2

        self.width = width
        self.height = height

        for child in self.children:
            child.origin = child.origin + (delta_x, delta_y)

        for connection in self.connections:
            connection.origin = connection.origin + (delta_x, delta_y)

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

        if not self.border:
            return
        p = path.rect(0, 0, 1, 1)
        sw = self.get('sw', level)
        self.style.append(trafo.scale(sx=self.width, sy=self.height))
        self.style.append(trafo.translate(sw.x, sw.y))
        canvas.stroke(p, self.style)

class Line(Box):

    """ A Line object represents a single line of text """

    def __init__(self, string, size=text.size.normalsize, **kwargs):

        super().__init__(**kwargs)
        self.string = string
        self.size = size
        self.initialize()

    def initialize(self):

        t = text.text(0, 0, self.string, [text.halign.left, text.valign.bottom, self.size])
        bb = t.bbox()
        self.width = 100*bb.width().t
        self.height = 100*bb.height().t

    def _draw(self, canvas, level=0):

        po = self.get('sw', level)
        x, y = po.x, po.y
        t = text.text(x, y, self.string, [text.halign.left, text.valign.bottom, self.size])
        canvas.insert(t)

class Connection(Box):

    def __init__(self, points=[], style=None):

        super().__init__()

        self.points = points if points else []
        self.style  = style  if style  else []
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
        canvas.stroke(p, self.style)
