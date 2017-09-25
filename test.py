from metapyx import *

poem = """Cuanto te habra dolido acostumbrarte a mi,
a mi alma sola y salvaje, a mi nombre que todos ahuyentan.
Hemos visto arder tantas veces el lucero besandonos los ojos
y sobre nuestras cabezas destorcerse los crepusculos en abanicos girantes."""

def poem_lines():
    return poem.split('\n')

if __name__ == '__main__':

    cvs = pyx.canvas.canvas()

    ll = poem_lines()

    ts = []
    ok_ts = []
    for i in range(0, 10):
        ts.append(Text(*ll, alignment=Align.left))

    for t, pair in zip(ts, Text.Size_ratios.items()):
        _, ratio = pair
        try:
            t.scale(ratio)
            ok_ts.append(t)
        except Text.ScalingError:
            print("Could not scale by {}".format(ratio))

    top_to_bottom(*ok_ts, alignment=Align.left)

    for t in ok_ts:
        t.rotate(45)

    for t in ok_ts:
        t.draw(cvs)

    cvs.writeSVGfile("test")
