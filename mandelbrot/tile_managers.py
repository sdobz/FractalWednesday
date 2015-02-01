from .base import TileManager
from os import path
import logging
import numpy as np
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class CachelessTileManager(TileManager):
    def get_tile_data(self, tile):
        return self.generate_tile_data(tile)


class NumpyCompressedTileManager(TileManager):
    root = 'data/'

    def get_tile_data(self, tile):
        data = self.generate_tile_data(tile)

        log.debug("""Getting mandelbrot image
        x: {}, y: {}, z: {}""".format(tile.x, tile.y, tile.z))
        filename = self.root + self.get_tile_key(tile) + '.npz'

        if path.exists(filename):
            return np.load(filename)['mandel_data']

        np.savez_compressed(filename, mandel_data=data)
        return data
