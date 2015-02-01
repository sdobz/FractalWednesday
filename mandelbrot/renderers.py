from PIL import Image
import numpy as np
from .base import Renderer
import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class NumpyColorRenderer(Renderer):
    def color_data(self, generator, data):
        palette = self.palette
        iterations = generator.iterations
        max_color = self.max_color

        palette_length = len(palette)

        @np.vectorize
        def colorize_matrix(i):
            if i == iterations:
                return max_color
            else:
                return palette[i % palette_length]

        colorized_data = colorize_matrix(data)
        # starts as a 3 tuple of dpuxdpu integers
        colorized_data = np.uint8(np.array(colorized_data))
        # Turns it into an array of uint8s
        colorized_data = np.rollaxis(colorized_data, axis=0, start=3)
        # Starts (3, 400, 400), rollaxis moves the color to the last place (400, 400, 3)

        return colorized_data

from PIL import ImageDraw


class PILRenderer(NumpyColorRenderer):
    resample_method = Image.LANCZOS
    debug = True

    @staticmethod
    def print_thing(name, func, *things, **named_things):
        out = func(*things, **named_things)
        print(name)
        print(out)
        return out

    def add_debug_info(self, renderset, img):
        if self.debug:
            apparent_tile_size = renderset.apparent_tile_size
            draw = ImageDraw.Draw(img)

            draw.text((10, 10), 'S: {}'.format(apparent_tile_size), fill='green')

            draw.line((self.w/2, 0, self.w/2, self.h), fill='white')
            draw.line((0, self.h/2, self.w, self.h/2), fill='white')

            for tile in renderset.data_tiles:
                draw.rectangle((tile.pix_x, tile.pix_y,
                                tile.pix_x + apparent_tile_size, tile.pix_y + apparent_tile_size), outline='green')

                draw.text((tile.pix_x+3, tile.pix_y+3), "Tile: {}, {}, {}".format(tile.x, tile.y, tile.z), fill='red')

        return img

    def render_renderset(self, renderset):
        apparent_tile_size = renderset.apparent_tile_size
        img = Image.new('RGB', (self.w, self.h), self.max_color)
        for tile in renderset.data_tiles:
            img.paste(
                im=Image.fromarray(self.color_data(self.tile_manager.generator, self.tile_manager.get_tile_data(tile)), 'RGB').resize(
                    size=(apparent_tile_size, apparent_tile_size),
                    resample=self.resample_method),
                box=(tile.pix_x, tile.pix_y)
            )
        return np.asarray(self.add_debug_info(renderset, img))
