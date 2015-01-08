from __future__ import division
from mandelbrot import generate_viewport, gen_palette
import md5
import colorsys
from moviepy.video.VideoClip import VideoClip
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
import numpy as np


class Mandelbrot:
    max_i = 1000
    dpu = 256
    palette = None
    gen_palette = staticmethod(gen_palette)
    cache = {}

    def __init__(self, w, h):
        log.info("Initializing Mandelbrot generator {}x{} with {}px chunks, max {} iterations".format(w, h, self.dpu, self.max_i))
        self.w = w
        self.h = h

    @staticmethod
    def javascript_palette():
        cycle_size = 20
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

        """
        for i in xrange(cycle_size):
            m = (i % cycle_size)/cycle_size
            if m < 0.5:
                h = 240 # blue
                # black to white
                l = m * 200
            else:
                h = 30 # orange
                l = 100 - (m - 0.5 * 200)

            log.warn("H: {} S: {} L: {} M:".format(h, 0.5, l, m))
            r, g, b = colorsys.hls_to_rgb(h/255, l/100, 0.5)

            palette.append((r*255, g*255, b*255))
        """
        palette = [(np.uint8(r*255), np.uint8(g*255), np.uint8(b*255)) for r, g, b in palette]
        log.warn("Using palette: {}".format(palette))
        return palette

    def gen_viewport(self, x, y, z):
        if not self.palette:
            # self.palette = gen_palette()
            self.palette = self.javascript_palette()

        return generate_viewport(x, y, z, dpu=self.dpu, w=self.w, h=self.h, max_i=self.max_i, palette=self.palette)

    def cache_key(self, x, y, z):
        return md5.new('{}{}{}'.format(x, y, z)).digest()


class MandelbrotClip:
    def __init__(self, size, duration):
        self.mandelbrot = Mandelbrot(size[0], size[1])
        self.mandelbrot_size = size
        self.duration = duration

        self.videoclip = VideoClip(duration=duration)

    def fly_to(self, x0, y0, x1, y1):
        pass

    def make_index_to(self, x, y, start_z, end_z):
        def gen_frame(t):
            log.debug("Making frame at t={}".format(t))
            if self.duration:
                z_t = end_z - (start_z - end_z) * (t-self.duration)/self.duration
                log.debug("Z: {}".format(z_t))
            else:
                z_t = 0

            return self.mandelbrot.gen_viewport(x, y, z_t)

        self.videoclip = self.videoclip.set_make_frame(gen_frame)
        pass


video = MandelbrotClip(size=(1280, 720), duration=20)

#video.make_index_to(-1.772, 0.013, -5, 15)
#video.make_index_to(-0.75538, 0.11220, -3, 15)
video.make_index_to(0.3750001200618655, -0.2166393884377127, -3, 15)
#video.make_index_to(-0.13856524454487512487, -0.64935990749191975, -3, 20)
#video.make_index_to(0.001643721971153, 0.822467633298876, -3, 50)
#video.make_index_to(-0.75, -.1, -1.5, 20)
video.videoclip.write_videofile('RealZoom.mp4', fps=25, preset='medium', threads=3)
#video.videoclip.write_images_sequence(nameformat='output/frame%03d.png', fps=5)
