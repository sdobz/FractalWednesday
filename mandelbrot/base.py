from .util import transform_index


class ToImplement(Exception):
    pass


class TileManager(object):
    def __init__(self, generator):
        self.generator = generator

    def generate_tile_data(self, tile):
        return self.generator.generate_tile(tile.x, tile.y, tile.z)

    def get_tile_data(self, tile):
        raise ToImplement


class Renderer(object):
    def __init__(self, size, palette, max_color, tile_manager):
        self.w = size[0]
        self.h = size[1]
        self.palette = list(palette)
        self.max_color = max_color
        self.tile_manager = tile_manager

    def render_renderset(self, renderset):
        raise ToImplement


class Generator(object):
    """
    A stub generator that doesn't do much
    """
    def __init__(self, iterations, tile_size):
        self.iterations = iterations
        self.tile_size = tile_size

    def generate_tile(self, x, y, z):
        u0, v0 = transform_index(x, y, z)
        u1, v1 = transform_index(x+1, y+1, z)

        return self.generate_region(u0, u1, v0, v1)

    def generate_region(self, u0, u1, v0, v1):
        raise ToImplement
