from .composer import Composer
from .base import Generator, TileManager, Renderer


class Mandelbrot(object):
    """
    This class contains the process of forming the mandelbrot fractal
    It uses a bunch of other classes to do the heavy lifting. These classes should be swappable

    High level:
    Instance with: iterations, tile_size
    Input: u, v, z, w, h

    Where u and v are the real and complex parts of the input position
    And z is the pixel scale.
    At z=0: 0 to tile_size pixels map to 0 to 1
    At z=1: 0 to tile_size pixels map to 0 to 0.5
    At z=n: 0 to tile_size pixels map to 0 to 1/2**z
    Every time z increases by 1 the pixel density doubles

    Given that input
    If color: check for color
    Check storage for data tile cache
    Generate a tile
    Save the tile
    If color: color tile
    Compose tiles
    Return view
    """

    def __init__(self, size, palette, max_color, iterations, tile_size, generator, tile_manager, renderer):
        self.renderer = renderer(
            size=size,
            palette=palette,
            max_color=max_color,
            tile_manager=tile_manager(
                generator=generator(
                    iterations=iterations,
                    tile_size=tile_size
                )
            )
        )
        self.composer = Composer(size=size, tile_size=tile_size)

    def render_frame(self, u, v, z):
        return self.renderer.render_renderset(self.composer.generate_renderset(u, v, z))
