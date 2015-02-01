from __future__ import division
from math import floor, ceil
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

from .util import transform_real, RenderSet, DataTile

"""
Composers take tiles and put them together, applying a palette in the process
"""


class Composer(object):
    """
    The base composer does not know how to actually put tiles together, but it can generate the set of tiles required to
    fit a viewport.
    """

    def __init__(self, size, tile_size):
        self.w = size[0]
        self.h = size[1]
        self.tile_size = tile_size

    def generate_renderset(self, u, v, z):
        """
        Generates a ViewPort containing tiles that are required to fit a viewport at u, v
        using the classes width, height, and tile_size
        :param u: x-like component of the fractal
        :param v: y-like component of the fractal
        :param z: viewport z
        :return: ViewPort: A ViewPort of the above
        """

        # Store some local data for the function
        w, h, base_tile_size = self.w, self.h, self.tile_size

        # The z value of tiles that are at >= resolution the z value specified
        tile_z = int(ceil(z))

        # Transform the u v coordinates into index space
        x, y = transform_real(u, v, tile_z)

        # Half the screen width in tile_size units
        half_index_width = w/base_tile_size/2
        half_index_height = h/base_tile_size/2

        # The floors of the window bounds
        min_x, max_x = int(floor(x - half_index_width)), int(floor(x + half_index_width))
        min_y, max_y = int(ceil(y - half_index_height)), int(ceil(y + half_index_height))

        log.debug("""Generating tile_list
                  X, Y = {}, {}
                  {}x{}
                  X: {}->{}
                  Y: {}->{}""".format(x, y, w, h, min_x, max_x, min_y, max_y))

        # The list of tiles you need to fill out the requested viewport
        return self.layout_tiles(z, tile_z, x, y,
                                 tile_coords=[(x, y) for x in xrange(min_x, max_x+1) for y in xrange(min_y, max_y+1)])

    def layout_tiles(self, z, tile_z, x, y, tile_coords):
        """
        """
        # Let me just tuck this in here, it's the hard part
        apparent_tile_size = int(round(self.tile_size / 2**(ceil(z%1) - z%1)))

        return RenderSet(apparent_tile_size=apparent_tile_size,
                         data_tiles=[
                             DataTile(
                                 x=tile_coord[0],
                                 y=tile_coord[1],
                                 z=tile_z,
                                 pix_x=int(round((tile_coord[0]-x) *  apparent_tile_size + self.w/2)),
                                 pix_y=int(round((tile_coord[1]-y) * -apparent_tile_size + self.h/2)))
                             for tile_coord in tile_coords
                         ])
