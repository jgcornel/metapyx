from enum import Enum
from metapyx import *

class Alignment(Enum):
    left    =   1
    right   =   2
    center  =   3
    bottom  =   4
    middle  =   5
    top     =   6

class Direction(Enum):
    left    =   1
    right   =   2
    up      =   3
    down    =   4

def left_to_right(alignment, delta, anchor_box, *boxes):

    if not boxes:
        return

    box = boxes[0]

    if alignment is Alignment.bottom:
        box.sw = anchor_box.se + (delta, 0)
    elif alignment is Alignment.middle:
        box.w  = anchor_box.e  + (delta, 0)
    elif alignment is Alignment.top:
        box.nw = anchor_box.ne + (delta, 0)
    else:
        raise(RuntimeError('Invalid Alignment: {}'.format(alignment)))

    left_to_right(alignment, delta, boxes[0], *(boxes[1:]))

def right_to_left(alignment, delta, anchor_box, *boxes):

    if not boxes:
        return

    box = boxes[0]

    if alignment is Alignment.bottom:
        box.se = anchor_box.sw - (delta, 0)
    elif alignment is Alignment.middle:
        box.e  = anchor_box.w  - (delta, 0)
    elif alignment is Alignment.top:
        box.ne = anchor_box.nw - (delta, 0)
    else:
        raise(RuntimeError('Invalid Alignment: {}'.format(alignment)))

    right_to_left(alignment, delta, boxes[0], *(boxes[1:]))

def bottom_to_top(alignment, delta, anchor_box, *boxes):

    if not boxes:
        return

    box = boxes[0]

    if alignment is Alignment.left:
        box.sw = anchor_box.nw + (0, delta)
    elif alignment is Alignment.center:
        box.s  = anchor_box.n  + (0, delta)
    elif alignment is Alignment.right:
        box.se = anchor_box.ne + (0, delta)
    else:
        raise(RuntimeError('Invalid Alignment: {}'.format(alignment)))

    bottom_to_top(alignment, delta, boxes[0], *(boxes[1:]))


def top_to_bottom(alignment, delta, anchor_box, *boxes):

    if not boxes:
        return

    box = boxes[0]

    if alignment is Alignment.left:
        box.nw = anchor_box.sw - (0, delta)
    elif alignment is Alignment.center:
        box.n  = anchor_box.s  - (0, delta)
    elif alignment is Alignment.right:
        box.ne = anchor_box.se - (0, delta)
    else:
        raise(RuntimeError('Invalid Alignment: {}'.format(alignment)))

    top_to_bottom(alignment, delta, boxes[0], *(boxes[1:]))

def partition_segment(start, stop, fraction):

    point = Point(0, 0)

    point.x = start.x + fraction * (stop.x - start.x)
    point.y = start.y + fraction * (stop.y - start.y)

    return point
