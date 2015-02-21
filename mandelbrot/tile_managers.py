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
        log.debug("""Getting mandelbrot image
        x: {}, y: {}, z: {}""".format(tile.x, tile.y, tile.z))
        filename = self.root + self.get_tile_key(tile) + '.npz'

        if path.exists(filename):
            return np.load(filename)['mandel_data']

        data = self.generate_tile_data(tile)
        np.savez_compressed(filename, mandel_data=data)
        return data


from hashlib import md5
import ZODB
from BTrees.OOBTree import BTree
import transaction
import ZODB.FileStorage, zc.zlibstorage


class ZODBTileManager(TileManager):
    def __init__(self, *args, **kwargs):
        storage = zc.zlibstorage.ZlibStorage(
            ZODB.FileStorage.FileStorage('data/zodb.fs'))
        db = ZODB.DB(storage)
        connection = db.open()
        root = connection.root
        root.tile_data = BTree()
        self.tile_data = root.tile_data

        super(ZODBTileManager, self).__init__(*args, **kwargs)

    def get_tile_data(self, tile):
        key = md5(self.get_tile_key(tile)).digest()
        if key in self.tile_data:
            log.info('Got tile data')
            return self.tile_data[key]

        data = self.generate_tile_data(tile)

        self.tile_data[key] = data
        transaction.commit()
        return data


