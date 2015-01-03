from mandelbrot import generate_viewport, gen_palette
import md5
from moviepy.video.VideoClip import VideoClip
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)



class Mandelbrot:
    max_i = 400
    dpu = 512
    palette = None
    gen_palette = staticmethod(gen_palette)
    cache = {}

    def __init__(self, w, h):
        log.info("Initializing Mandelbrot generator {}x{} with {}px chunks, max {} iterations".format(w, h, self.dpu, self.max_i))
        self.w = w
        self.h = h

    def gen_viewport(self, x, y, z):
        cache_key = self.cache_key(x, y, z)

        if cache_key in self.cache:
            return self.cache[cache_key]

        if not self.palette:
            self.palette = gen_palette()

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

    def make_index_to(self, x, y, z):
        def gen_frame(t):
            log.debug("Making frame at t={}".format(t))
            z_t = z * (self.duration - t)/self.duration

            return self.mandelbrot.gen_viewport(x, y, z_t)

        self.videoclip = self.videoclip.set_make_frame(gen_frame)
        pass


video = MandelbrotClip(size=(320, 240), duration=2)
video.make_index_to(-0.6483906250000001, 0.4554739583333333, 9)
video.videoclip.write_videofile('out1.webm', 30, preset='ultrafast', threads=2)
