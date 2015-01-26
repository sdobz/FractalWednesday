from .base import TileManager


class CachelessTileManager(TileManager):
    def get_tile_data(self, tile):
        return self.generate_tile_data(tile)