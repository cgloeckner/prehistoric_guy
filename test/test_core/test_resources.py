import pygame
import unittest

from core import resources


def color_to_hex(color: pygame.Color) -> str:
    hex_string = "#{0:02x}{1:02x}{2:02x}".format(
        color.r,
        color.g,
        color.b,
    )
    return hex_string


class ResourcesTest(unittest.TestCase):
    def setUp(self):
        pygame.init()

    def tearDown(self):
        pygame.quit()

    # --- transform_image_hsl ------------------------------------------------------------------------------------------

    # Case 1: all non-transparent pixels are replaced
    def test__transform_image_hsl__1(self):
        surface = pygame.Surface((5, 5), flags=pygame.SRCALPHA)
        green_rect = pygame.Rect(1, 1, 2, 1)
        pygame.draw.rect(surface, 'green', green_rect)
        red_rect = pygame.Rect(0, 0, 4, 3)
        pygame.draw.rect(surface, 'red', red_rect)

        color = pygame.Color('black')
        color.hsla = 180, 76, 50, 100
        hex_str = color_to_hex(color)

        transform = resources.HslTransform(hue=180, saturation=76, lightness=50)
        resources.transform_image_hsl(surface, transform)

        pixels = pygame.PixelArray(surface)
        for y in range(surface.get_height()):
            for x in range(surface.get_width()):
                if pixels[x, y] & 0xff000000 == 0:
                    # ignore transparent pixels
                    continue

                hex = color_to_hex(surface.unmap_rgb(pixels[x, y]))
                self.assertEqual(hex, hex_str)

    # Case 2: all red and blue pixels are replaced
    def test__transform_image_hsl__2(self):
        surface = pygame.Surface((5, 5), flags=pygame.SRCALPHA)
        green_rect = pygame.Rect(1, 1, 2, 1)
        pygame.draw.rect(surface, 'green', green_rect)
        red_rect = pygame.Rect(0, 0, 3, 2)
        pygame.draw.rect(surface, 'red', red_rect)
        blue_rect = pygame.Rect(4, 4, 1, 1)
        pygame.draw.rect(surface, 'blue', blue_rect)

        color = pygame.Color('black')
        color.hsla = 180, 76, 50, 100
        hex_str = color_to_hex(color)

        transform = resources.HslTransform(hue=180, saturation=76, lightness=50)
        resources.transform_image_hsl(surface, transform, ['red', 'blue'])

        # assert: all red pixels are altered
        pixels = pygame.PixelArray(surface)
        for y in range(surface.get_height()):
            for x in range(surface.get_width()):
                if pixels[x, y] & 0xff000000 == 0:
                    # ignore transparent pixels
                    continue

                hex = color_to_hex(surface.unmap_rgb(pixels[x, y]))
                if blue_rect.collidepoint(x, y) or red_rect.collidepoint(x, y):
                    self.assertEqual(hex, hex_str)
                else:
                    # stayed green
                    self.assertEqual(hex, '#00ff00')

    # --- fill_pixels --------------------------------------------------------------------------------------------------

    def test__fill_pixels(self):
        surface = pygame.Surface((5, 5), flags=pygame.SRCALPHA)
        green_rect = pygame.Rect(1, 1, 2, 1)
        pygame.draw.rect(surface, 'green', green_rect)

        color = pygame.Color('black')
        color.hsla = 180, 76, 50, 100
        hex_str = color_to_hex(color)

        resources.fill_pixels(surface, color)

        pixels = pygame.PixelArray(surface)
        for y in range(surface.get_height()):
            for x in range(surface.get_width()):
                if pixels[x, y] & 0xff000000 == 0:
                    # ignore transparent pixels
                    continue

                hex = color_to_hex(surface.unmap_rgb(pixels[x, y]))
                self.assertEqual(hex, hex_str)
