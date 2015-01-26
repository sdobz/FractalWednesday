"""
The intent of this module is to make generating palettes easier. Dunno how that's going to work yet
"""
from __future__ import division
import numpy as np
import colorsys
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def blue_black_orange_white(cycle_size):
    palette = []

    # Mid tone
    s = 0.81
    # Blue cycle
    h = 200/360
    for i in xrange(cycle_size):
        l = i/cycle_size
        log.debug("H: {} L: {} S: {}".format(h, l, s))
        color = colorsys.hls_to_rgb(h, l, s)
        log.debug('Color: {}'.format(color))
        palette.append(color)

    # Orange cycle
    h = 30/360
    for i in xrange(cycle_size):
        l = 1-(i/cycle_size)
        color = colorsys.hls_to_rgb(h, l, s)
        palette.append(color)

    return [(np.uint8(r*255), np.uint8(g*255), np.uint8(b*255)) for r, g, b in palette]
