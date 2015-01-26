from collections import namedtuple


def transform_index(x, y, z):
    # Takes index and returns real
    return x/(2**z), y/(2**z)


def transform_real(u, v, z):
    # Takes real and returns index
    return (2**z)*u, (2**z)*v


RenderSet = namedtuple('RenderSet', 'apparent_tile_size data_tiles')
DataTile = namedtuple('DataTile', 'x y z pix_x pix_y')
