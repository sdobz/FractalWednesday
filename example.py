from mandelbrot import Mandelbrot
from mandelbrot.generators import NumexprGenerator
from mandelbrot.renderers import PILRenderer
from mandelbrot.palettes import blue_black_orange_white
from mandelbrot.tile_managers import CachelessTileManager

from moviepy.video.VideoClip import VideoClip
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def render_video(destination, start_z, end_z, size, duration, fps, filename):
    proc = Mandelbrot(
        renderer=PILRenderer,
        size=size,
        palette=blue_black_orange_white(cycle_size=30),
        max_color=(0, 0, 0),
        tile_manager=CachelessTileManager,
        generator=NumexprGenerator,
        iterations=1000,
        tile_size=512
    )

    def gen_frame(t):
        log.debug("Making frame at t={}".format(t))
        if duration:
            z_t = end_z - (start_z - end_z) * (t-duration)/duration
            log.debug("Z: {}".format(z_t))
        else:
            z_t = 0

        return proc.render_frame(destination[0], destination[1], z_t)

    VideoClip(duration=duration)\
        .set_make_frame(gen_frame)\
        .write_videofile(
            filename=filename,
            fps=fps,
            preset='medium',
            threads=3)



render_video(destination=(-0.7483306070963540, 0.1492396240234374),
             start_z=-3,
             end_z=15,
             size=(1280, 720),
             duration=0,
             fps=1,
             filename='TriciaZoom2.mp4')
