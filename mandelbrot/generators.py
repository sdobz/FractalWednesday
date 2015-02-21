"""
This module generates mandelbrot data
"""
from collections import namedtuple
from .base import Generator
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

ComplexTile = namedtuple('ComplexTile', 'u0 u1 v0 v1 step_size')

import numexpr as ne
import numpy as np


class NumexprGenerator(Generator):
    # Check out:
    # https://github.com/Arachnid/exabrot/blob/master/mandelbrot.py

    # Using:
    # http://www.vallis.org/salon/summary-10.html
    def generate_region(self, u0, u1, v0, v1):
        """Compute an tile_size x tile_size Mandelbrot matrix with maxi maximum iterations."""

        tile_size, iterations = self.tile_size, self.iterations

        log.debug("""Mandelbrot parameters:
                  X {}->{}
                  Y {}->{}
                  {}px, i={}""".format(u0, u1, v0, v1, tile_size, iterations))

        xs, ys = np.meshgrid(np.linspace(u0, u1, tile_size), np.linspace(v0, v1, tile_size))

        z = np.zeros((tile_size, tile_size), 'complex128')
        c = xs + 1j*ys

        escape = np.empty((tile_size, tile_size), 'int32')
        escape[:,:] = iterations

        for i in xrange(1, iterations):
            # we're just wrapping the numpy expression with `evaluate`
            mask = ne.evaluate('escape == iterations')

            # boolean indexing is not too numexpr-friendly, so instead we use
            # the numpy function `where(cond,then,else)` and set z to 0
            # at already-escaped points, to avoid overflows
            z = ne.evaluate('where(mask,z**2+c,0)')

            # again where; taking the real part of abs is necessary here
            # because in numexpr abs(complex) is complex with 0 imaginary part
            escape = ne.evaluate('where(mask & (abs(z).real > 2),i,escape)')

        return escape


class PerturbedGenerator(Generator):

    def generate_region(self, u0, u1, v0, v1):
        tile_size, iterations = self.tile_size, self.iterations
        log.debug("""Mandelbrot parameters:
                  X {}->{}
                  Y {}->{}
                  {}px, i={}""".format(u0, u1, v0, v1, tile_size, iterations))

        dn = np.zeros((tile_size, tile_size), 'complex128')

        escape = np.empty((tile_size, tile_size), 'int32')
        escape[:,:] = iterations

        # A number in the center of our viewport
        xn = (u0 + u1) / 2 + 1j * ((v0 + v1) / 2)
        x0 = xn
        an = 0 + 0j
        bn = 0 + 0j
        cn = 0 + 0j

        yi0, yj0 = np.meshgrid(np.linspace(u0, u1, tile_size), np.linspace(v0, v1, tile_size))
        d0 = (yi0 + 1j*yj0) - x0

        for i in xrange(1, iterations):
            try:
                cn = 2*xn*cn + 2*an*bn
                bn = 2*xn*bn + an**2
                an = 2*xn*an + 1
                xn = xn**2 + x0
            except OverflowError:
                log.debug("I give up.")
                break

            # we're just wrapping the numpy expression with `evaluate`
            mask = ne.evaluate('escape == iterations')

            # boolean indexing is not too numexpr-friendly, so instead we use
            # the numpy function `where(cond,then,else)` and set z to 0
            # at already-escaped points, to avoid overflows
            dn = ne.evaluate('where(mask,an*d0 + bn*d0 + cn*d0,0)')

            # again where; taking the real part of abs is necessary here
            # because in numexpr abs(complex) is complex with 0 imaginary part
            escape = ne.evaluate('where(mask & (abs(dn+xn).real > 2),i,escape)')

        return escape
