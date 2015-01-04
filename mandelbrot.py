#!/usr/bin/env python


# make integer division return a float
from __future__ import division
import numpy as np
import numexpr as ne
import matplotlib.pyplot as plt
from math import floor, ceil
from os import path
import colorsys
from PIL import Image, ImageDraw
import logging
logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)


# Data root with trailing slash
DATA_ROOT = 'data/'
MAX_ITERATION_COLOR = (0, 0, 0)
RESIZE_METHOD = Image.LANCZOS

DEBUG = log.getEffectiveLevel() == logging.DEBUG


def generate_viewport(u, v, z, dpu, w, h, max_i, palette):
    return np.asarray(generate_pil_viewport(u, v, z, dpu, w, h, max_i, palette))


def generate_pil_viewport(u, v, z, dpu, w, h, max_i, palette):
    log.info("Generating PIL viewport...")

    tile_z = int(ceil(z))
    x, y = transform_real(u, v, tile_z)
    tile_size = dpu / 2**(ceil(z%1) - z%1)
    tile_coord_list = generate_tileset_coords(x, y, tile_size, w, h)
    log.debug(tile_coord_list)
    tiles = []

    for tile_x, tile_y in tile_coord_list:
        tiles.append(Image.fromarray(get_colored_mandelbrot_matrix(tile_x, tile_y, tile_z, dpu, max_i, palette), 'RGB'))

    img = Image.new('RGB', (w, h), MAX_ITERATION_COLOR)

    for tile, tile_coords in zip(tiles, tile_coord_list):
        tile_x, tile_y = tile_coords

        tile_viewport_x = (tile_x-x) * tile_size + w/2
        tile_viewport_y = (tile_y-y) * tile_size + h/2

        tile_viewport_x = int(floor(tile_viewport_x))
        tile_viewport_y = int(floor(tile_viewport_y))

        # log.debug("Transform: X: {}->{} Y: {}->{}".format(tile_viewport_x, tile_viewport_x + tile_size, tile_viewport_y, tile_viewport_y + tile_size))

        tile_size_int = int(floor((tile_size)))
        tile_resized = tile.resize((tile_size_int, tile_size_int), RESIZE_METHOD)

        img.paste(tile_resized, (tile_viewport_x, tile_viewport_y))

    if DEBUG:
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "U: {}, V: {}".format(u, v), fill='red')
        draw.text((10, 20), "Z: {}, X: {}, Y: {}".format(z, x, y), fill='red')
        draw.text((10, 30), "Tile size: {} -> {}".format(dpu, tile_size_int), fill='red')

        draw.line((w/2, 0, w/2, h), fill='red')
        draw.line((0, h/2, w, h/2), fill='red')

        for tile_x, tile_y in tile_coord_list:
            tile_viewport_x = (tile_x-x) * tile_size + w/2
            tile_viewport_y = (tile_y-y) * tile_size + h/2

            draw.rectangle((tile_viewport_x, tile_viewport_y, tile_viewport_x + tile_size_int, tile_viewport_y + tile_size_int), outline='green')

            draw.text((tile_viewport_x+10, tile_viewport_y+10), "Tile: {}, {}, {}".format(tile_x, tile_y, tile_z), fill='red')

    return img


mandelbrot_colored_memcache = {}
def get_colored_mandelbrot_matrix(tile_x, tile_y, tile_z, dpu, max_i, palette):
    filename = index_to_filename(tile_x, tile_y, tile_z, dpu, max_i) + '.png'

    if filename in mandelbrot_colored_memcache:
        return mandelbrot_colored_memcache[filename]

    mandelbrot_colored_memcache[filename] = generate_colored_mandelbrot_matrix(tile_x, tile_y, tile_z, dpu, max_i, palette)
    return mandelbrot_colored_memcache[filename]


def generate_tileset_coords(x, y, tile_size, w, h):
    # I transform from screen space (pixels) into index space (where 1 = 1 dpus worth of pixels)
    half_index_width = w/tile_size/2
    half_index_height = h/tile_size/2
    log.debug(half_index_width)

    # int is also flooring
    min_x, max_x = int(floor(x - half_index_width)), int(floor(x + half_index_width))
    min_y, max_y = int(floor(y - half_index_height)), int(floor(y + half_index_height))

    log.debug("""Generating Coordinates
              X, Y = {}, {}
              {}x{}
              X: {}->{}
              Y: {}->{}""".format(x, y, w, h, min_x, max_x, min_y, max_y))

    return [(x, y) for x in xrange(min_x, max_x+1) for y in xrange(min_y, max_y+1)]


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
    log.debug("""Getting mandelbrot image
    x: {}, y: {}, z: {}""".format(x, y, z))
    filename = index_to_filename(x, y, z, dpu, max_i) + '.npz'

    if path.exists(filename):
        return np.load(filename)['mandel_data']

    mandel_data = generate_indexed_mandelbrot_matrix(x, y, z, dpu, max_i)
    np.savez_compressed(filename, mandel_data=mandel_data)
    return mandel_data


def generate_indexed_mandelbrot_matrix(x, y, z, dpu, max_i):
    log.warn("Generating new mandelbrot {},{},{}".format(x, y, z))
    u0, v0 = transform_index(x, y, z)
    u1, v1 = transform_index(x+1, y+1, z)

    return generate_mandelbrot_matrix(u0, u1, v0, v1, dpu, max_i)


def transform_index(x, y, z):
    # Takes index and returns real
    return x/(2**z), y/(2**z)


def transform_real(u, v, z):
    # Takes real and returns index
    return (2**z)*u, (2**z)*v


# Check out:
# https://github.com/Arachnid/exabrot/blob/master/mandelbrot.py

# Using:
# http://www.vallis.org/salon/summary-10.html
def generate_mandelbrot_matrix(u0, u1, v0, v1, dpu, max_i):
    """Compute an dpu x dpu Mandelbrot matrix with maxi maximum iterations."""

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

    log.debug(escape)

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

def imshow(img):
    plt.figure()
    plt.imshow(img)
    plt.show()


def draw_text(img, x, y, text, color='red'):
    draw = ImageDraw.Draw(img)
    draw.text((x, y), text, fill=color)


def show_viewport():
    #x, y, z = -0.5, 0.0, -2.5
    x, y, z = (-0.648390625, 0.455473958333, -1.5)

    dpu = 512

    # w, h = dpu * 3, dpu * 2
    w, h = 1260, 720

    palette = gen_palette()

    plt.figure()
    plt.imshow(generate_viewport(x, y, z, dpu=dpu, w=w, h=h, max_i=400, palette=palette), origin='lower')
    plt.show()

#show_viewport()

def show_colored_mandelbrot_matrix():
    x, y, z = 0, 0, 0

    palette = gen_palette()

    plt.figure()
    plt.imshow(np.array(generate_colored_mandelbrot_matrix(x, y, z, dpu=400, max_i=400, palette=palette)), origin='lower')
    plt.show()

# show_colored_mandelbrot_matrix()


def show_indexed_mandelbrot_matrix():
    x, y, z = 0, 0, 0

    x0, y0 = transform_index(x, y, z)
    x1, y1 = transform_index(x+1, y+1, z)

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


