"""
This module generates mandelbrot data
"""
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

import numexpr as ne
import numpy as np


class Generator(object):
    """
    A stub generator that doesn't do much
    """
    tile_size = 512
    iterations = 400

    def __init__(self, iterations=None, tile_size=None):
        if iterations:
            self.iterations = iterations
        if tile_size:
            self.tile_size = tile_size

    def generate_tile(self, x, y, z):
        raise NotImplemented


class NumexprGenerator(Generator):
    def generate_tile(self, x, y, z):
        log.warn("Generating new mandelbrot {},{},{}".format(x, y, z))
        u0, v0 = transform_index(x, y, z)
        u1, v1 = transform_index(x+1, y+1, z)

        return self.generate_mandelbrot_matrix(u0, u1, v0, v1)

    # Check out:
    # https://github.com/Arachnid/exabrot/blob/master/mandelbrot.py

    # Using:
    # http://www.vallis.org/salon/summary-10.html
    def generate_mandelbrot_matrix(self, u0, u1, v0, v1):
        """Compute an dpu x dpu Mandelbrot matrix with maxi maximum iterations."""

        dpu, max_i = self.tile_size, self.iterations

        log.debug("""Mandelbrot parameters:
                  X {}->{}
                  Y {}->{}
                  {}px, i={}""".format(u0, u1, v0, v1, dpu, max_i))

        xs, ys = np.meshgrid(np.linspace(u0, u1, dpu), np.linspace(v0, v1, dpu))

        z = np.zeros((dpu, dpu), 'complex128')
        c = xs + 1j*ys

        escape = np.empty((dpu, dpu), 'int32')
        escape[:,:] = max_i

        for i in xrange(1, max_i):
            # we're just wrapping the numpy expression with `evaluate`
            mask = ne.evaluate('escape == max_i')

            # boolean indexing is not too numexpr-friendly, so instead we use
            # the numpy function `where(cond,then,else)` and set z to 0
            # at already-escaped points, to avoid overflows
            z = ne.evaluate('where(mask,z**2+c,0)')

            # again where; taking the real part of abs is necessary here
            # because in numexpr abs(complex) is complex with 0 imaginary part
            escape = ne.evaluate('where(mask & (abs(z).real > 2),i,escape)')

        return escape


def transform_index(x, y, z):
    # Takes index and returns real
    return x/(2**z), y/(2**z)


def transform_real(u, v, z):
    # Takes real and returns index
    return (2**z)*u, (2**z)*v
