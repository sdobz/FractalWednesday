from math import floor, ceil
from collections import namedtuple
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

from mandelbrot.util import transform_real

"""
Composers take tiles and put them together, applying a palette in the process
"""

ViewPort = namedtuple('ViewPort', 'u v z x y tile_z viewtile_set')
ViewTile = namedtuple('ViewTile', 'x y')

RenderSet = namedtuple('RenderSet', 'apparent_tile_size rendertile_set')
RenderTile = namedtuple('DataTile', 'pix_x pix_y data')


class MandelbrotComposer(object):
    """
    The base composer does not know how to actually put tiles together, but it can generate the set of tiles required to
    fit a viewport.
    """
    w = None
    h = None
    tile_size = None

    def __init__(self, w, h, tile_size):
        self.w = w
        self.h = h
        self.tile_size = tile_size

    def compose_viewport(self, u, v, z):
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
        min_y, max_y = int(floor(y - half_index_height)), int(floor(y + half_index_height))

        log.debug("""Generating tile_list
                  X, Y = {}, {}
                  {}x{}
                  X: {}->{}
                  Y: {}->{}""".format(x, y, w, h, min_x, max_x, min_y, max_y))

        # A tileset contained in the viewport
        return ViewPort(u=u, v=v, z=z, x=x, y=y, tile_z=tile_z,
                        viewtile_set=[ViewTile(x=x, y=y) for x in xrange(min_x, max_x+1) for y in xrange(min_y, max_y+1)])

    def compose_renderset(self, viewport):
        """
        Only required function for a composer. Given a viewport assemble the tiles. A viewport is defined as:
        :param x: viewport x (in index space)
        :param y: viewport y (in index space)
        :param z: viewport z
        :param tile_set: The set of tiles that
        :return: The composed viewport as a WxH RGB numpy object
        """
        z = viewport.z
        # Let me just tuck this in here, it's the hard part
        apparent_tile_size = int(round(self.tile_size / 2**(ceil(z%1) - z%1)))

        return self.compose_renderset(
            RenderSet(apparent_tile_size=apparent_tile_size,
                      rendertile_set=[RenderTile(pix_x=int(round((viewport.x-tile.x) * apparent_tile_size + self.w/2)),
                                                 pix_y=int(round((viewport.y-tile.y) * apparent_tile_size + self.h/2)))
                                      for tile in viewport.tile_set]))

    def render_renderset(self, renderset):
        """
        Compose a renderset into a WxH RGB numpy object
        :return:
        """
        raise NotImplemented


from PIL import Image
import numpy as np


class PILRenderer(MandelbrotComposer):
    background_color = (0, 0, 0)
    resize_method = Image.LANCZOS

    def render_renderset(self, renderset):
        apparent_tile_size = renderset.apparent_tile_size
        img = Image.new('RGB', (self.w, self.h), self.background_color)
        for tile in renderset.rendertile_set:
            tile_img = Image.fromarray(tile.data, 'RGB')
            tile_resized = tile_img.resize((apparent_tile_size, apparent_tile_size), self.resize_method)
            img.paste(tile_resized, (tile.pix_x, tile.pix_y))

        return np.asarray(img)
