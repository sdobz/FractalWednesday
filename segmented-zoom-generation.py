#!/usr/bin/env python


# make integer division return a float
from __future__ import division
import numpy as np
import numexpr as ne
import matplotlib.pyplot as plt
from math import floor, ceil
from os import path

# Data root with trailing slash
DATA_ROOT = 'data/'


def generate_image_list(x, y, dpu, w, h):
    # I transform from screen space (pixels) into index space (where 1 = 1 dpus worth of pixels)
    half_index_width = (w/2) / dpu
    half_index_height = (h/2) / dpu

    # int is also flooring
    min_x, max_x = int(floor(x - half_index_width)), int(ceil(x + half_index_width))
    min_y, max_y = int(floor(y - half_index_height)), int(ceil(y + half_index_height))

    return [(x, y) for x in xrange(min_x, max_x) for y in xrange(min_y, max_y)]


def generate_colored_mandelbrot_image(x, y, z, dpu, max_i, palette):
    mandel_data = get_indexed_mandelbrot_matrix(x, y, z, dpu, max_i)
    img = mandel_data.copy()

    palette_length = len(palette)
    for x in np.nditer(img, op_flags=['readwrite']):
        x[...] = palette[x % palette_length]

    return mandel_data


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


def show_colored_mandelbrot_matrix():
    x, y, z = 0, 0, 0

    palette = [np.linspace(0, 255, num=30, dtype=np.uint8), np.linspace(0, 255, num=30, dtype=np.uint8), np.linspace(0, 255, num=30, dtype=np.uint8)]

    plt.figure()
    plt.imshow(np.array(generate_colored_mandelbrot_image(x, y, z, dpu=400, max_i=400, palette=palette)), origin='lower')
    plt.show()

show_colored_mandelbrot_matrix()


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