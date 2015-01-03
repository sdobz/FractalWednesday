#!/usr/bin/env python


# make integer division return a float
from __future__ import division
import numpy as np
import numexpr as ne
import matplotlib.pyplot as plt
from math import floor, ceil
from os import path
import colorsys
from PIL import Image
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# Data root with trailing slash
DATA_ROOT = 'data/'
MAX_ITERATION_COLOR = (0, 0, 0)
RESIZE_METHOD = Image.LANCZOS


class Mandelbrot:
    max_i = 400
    dpu = 512
    gen_palette = staticmethod(gen_palette)

    def __init__(self, w, h):
        self.w = w
        self.h = h

    def generate_viewport(self, x, y, z):
        return generate_viewport(x, y, z, self.dpu, self.w, self.h, self.max_i, self.gen_palette())


def generate_viewport(x, y, z, dpu, w, h, max_i, palette):
    return np.asarray(generate_pil_viewport(x, y, z, dpu, w, h, max_i, palette), dtype=np.uint8)


def generate_pil_viewport(x, y, z, dpu, w, h, max_i, palette):
    log.info("""Generating PIL viewport at:
             x: {}, y: {}, z: {}
             dpu: {}, {}x{}""".format(x, y, z, dpu, w, h))
    tile_coord_list = generate_tileset_coords(x, y, dpu, w, h)
    tiles = []

    tile_z = int(ceil(z))

    for tile_x, tile_y in tile_coord_list:
        tiles.append(Image.new(generate_colored_mandelbrot_matrix(tile_x, tile_y, tile_z, dpu, max_i, palette), 'RGB'))

    img = Image.new('RGB', (w, h), MAX_ITERATION_COLOR)

    tile_scale = 1-(tile_z-z)
    tile_size = dpu * tile_scale

    for tile, tile_coords in zip(tiles, tile_coord_list):
        tile_x, tile_y = tile_coords

        tile_x_transform = w/2 + ((tile_x-x) * dpu)
        tile_y_transform = h/2 + ((tile_y-y) * dpu)

        tile_x_transform = int(round(tile_x_transform))
        tile_y_transform = int(round(tile_y_transform))

        tile_resized = tile.resize((tile_size, tile_size), RESIZE_METHOD)

        img.paste(tile_resized, (tile_x_transform, tile_y_transform))

    return img


def generate_tileset_coords(x, y, dpu, w, h):
    # I transform from screen space (pixels) into index space (where 1 = 1 dpus worth of pixels)
    half_index_width = (w/2) / dpu
    half_index_height = (h/2) / dpu

    # int is also flooring
    min_x, max_x = int(floor(x - half_index_width)), int(ceil(x + half_index_width))
    min_y, max_y = int(floor(y - half_index_height)), int(ceil(y + half_index_height))

    return [(x, y) for x in xrange(min_x, max_x) for y in xrange(min_y, max_y)]


def generate_colored_mandelbrot_matrix(x, y, z, dpu, max_i, palette):
    mandel_data = get_indexed_mandelbrot_matrix(x, y, z, dpu, max_i)

    palette_length = len(palette)

    @np.vectorize
    def colorize_matrix(i):
        if i == max_i:
            return MAX_ITERATION_COLOR
        else:
            return palette[i % palette_length]

    colorized_data = colorize_matrix(mandel_data)
    # starts as a 3 tuple of dpuxdpu integers
    colorized_data = np.uint8(np.array(colorized_data))
    # Turns it into an array of uint8s
    colorized_data = np.rollaxis(colorized_data, axis=0, start=3)
    # Starts (3, 400, 400), rollaxis moves the color to the last place (400, 400, 3)

    return colorized_data


def index_to_filename(x, y, z, dpu, max_i):
    # This is potentially irreversible (use a hash function to store x, y, z)
    return "{}mandelbrotX{}Y{}Z{}D{}I{}".format(DATA_ROOT, x, y, z, dpu, max_i)


def get_indexed_mandelbrot_matrix(x, y, z, dpu, max_i):
    filename = index_to_filename(x, y, z, dpu, max_i) + '.npz'

    if path.exists(filename):
        return np.load(filename)['mandel_data']

    mandel_data = generate_indexed_mandelbrot_matrix(x, y, z, dpu, max_i)
    np.savez_compressed(filename, mandel_data=mandel_data)
    return mandel_data


def generate_indexed_mandelbrot_matrix(x, y, z, dpu, max_i):
    x0, y0 = index_transform(x, y, z)
    x1, y1 = index_transform(x+1, y+1, z)

    return generate_mandelbrot_matrix(x0, x1, y0, y1, dpu, max_i)


def index_transform(x, y, z):
    return x/(2**z), y/(2**z)


def real_transform(x, y, z):
    return (2**z)*x, (2**z)*y


# Check out:
# https://github.com/Arachnid/exabrot/blob/master/mandelbrot.py

# Using:
# http://www.vallis.org/salon/summary-10.html
def generate_mandelbrot_matrix(x0, x1, y0, y1, dpu, max_i):
    """Compute an dpu x dpu Mandelbrot matrix with maxi maximum iterations."""

    xs, ys = np.meshgrid(np.linspace(x0, x1, dpu), np.linspace(y0, y1, dpu))

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


def gen_palette():
    colors_max = 1000

    palette = [0] * colors_max
    for i in xrange(colors_max):
        f = 0+abs((float(i)/colors_max-1)**15) # white on outside black on inside
        #f = 1-abs((float(i)/colors_max-1)**15) # black on outside white on inside
        r, g, b = colorsys.hsv_to_rgb(.8+f/3, 1-f/8, f)
        #r, g, b = colorsys.hsv_to_rgb(.64+f/3, 1-f/2, f)
        palette[i] = (int(r*255), int(g*255), int(b*255))

    return palette


def show_viewport():
    z = 1
    x, y = real_transform(-.5, 0, z)

    dpu = 512

    w, h = dpu * 3, dpu * 2

    palette = gen_palette()

    plt.figure()
    plt.imshow(generate_viewport(x, y, z, dpu=512, w=w, h=h, max_i=400, palette=palette), origin='lower')
    plt.show()

# show_viewport()

def show_colored_mandelbrot_matrix():
    x, y, z = 0, 0, 0

    palette = gen_palette()

    plt.figure()
    plt.imshow(np.array(generate_colored_mandelbrot_image(x, y, z, dpu=400, max_i=400, palette=palette)), origin='lower')
    plt.show()

# show_colored_mandelbrot_matrix()


def show_indexed_mandelbrot_matrix():
    x, y, z = 0, 0, 0

    x0, y0 = index_transform(x, y, z)
    x1, y1 = index_transform(x+1, y+1, z)

    plt.figure()
    plt.imshow(np.array(get_indexed_mandelbrot_matrix(x, y, z, dpu=400, max_i=400)), origin='lower', extent=(x0, x1, y0, y1))
    plt.show()

# show_indexed_mandelbrot_matrix()


def show_mandelbrot_matrix():
    x0, x1 = -2, 1
    y0, y1 = -1, 1

    plt.figure()
    plt.imshow(np.array(generate_mandelbrot_matrix(x0, x1, y0, y1, dpu=400, max_i=400)), origin='lower', extent=(x0, x1, y0, y1))
    plt.show()

# show_mandelbrot_matrix()