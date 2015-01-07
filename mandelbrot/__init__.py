

class MandelbrotProcess(object):
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

    # Classes I might need
    storage = None
    generator = None
    colorizer = None
    composer = None
    animator = None

    def generate_viewport(self, u, v, z):
