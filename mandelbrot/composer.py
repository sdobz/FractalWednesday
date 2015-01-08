from math import floor
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

"""
Composers take tiles and put them together, applying a palette in the process
"""


class MandelbrotComposer(object):
    """
    A stub composer that doesn't do any composing
    """
    w = None
    h = None

    def __init__(self, w, h, generator):
        self.w = w
        self.h = h
        self.generator = generator

    def generate_tiles_coords(self, x, y):
        # I transform from screen space (pixels) into index space (where 1 = 1 dpus worth of pixels)
        w, h, tile_size = self.w, self.h, self.generator.tile_size

        half_index_width = w/tile_size/2
        half_index_height = h/tile_size/2

        min_x, max_x = int(floor(x - half_index_width)), int(floor(x + half_index_width))
        min_y, max_y = int(floor(y - half_index_height)), int(floor(y + half_index_height))

        log.debug("""Generating Coordinates
                  X, Y = {}, {}
                  {}x{}
                  X: {}->{}
                  Y: {}->{}""".format(x, y, w, h, min_x, max_x, min_y, max_y))

        return [(x, y) for x in xrange(min_x, max_x+1) for y in xrange(min_y, max_y+1)]