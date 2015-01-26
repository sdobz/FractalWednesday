from PIL import Image
import numpy as np
from .base import Renderer


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


class PILRenderer(NumpyColorRenderer):
    resample_method = Image.LANCZOS

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

        return np.asarray(img)