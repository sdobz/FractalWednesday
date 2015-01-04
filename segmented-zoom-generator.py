from mandelbrot import generate_viewport, gen_palette
import md5
from moviepy.video.VideoClip import VideoClip
import logging
logging.basicConfig(level=logging.WARN)
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
#video.make_index_to(-1.772, 0.013, -3, 20)
#video.make_index_to(0.001643721971153, 0.822467633298876, -3, 20)
video.make_index_to(-0.75538,0.11220, -3, 20) #35)
video.videoclip.write_videofile('RealZoom.mp4', fps=25, preset='ultrafast', threads=3)

#video.videoclip.write_images_sequence(nameformat='output/frame%03d.png', fps=5)
