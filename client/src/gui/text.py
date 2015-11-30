from .base import *
from colors import *

class Text(GuiObject):
    def __init__(self, text, **params):
        self.text = text
        self.text_color = params.get("text_color", BLACK)
        self.font_size = params.get("font_size", 20)
        self.font = params.get("font", pygame.font.Font("..\\data\\fonts\\corbelb.ttf", self.font_size))
        params["size"] = self.font.size(self.text)
        self.bg_color = params.get("bg_color", None)
        self.border_color = params.get("border_color", None)
        GuiObject.__init__(self, **params)
        self.update_image()
    def update_image(self):
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        if self.bg_color:
            self.image.fill(self.bg_color)
        text_image = self.font.render(self.text, True, self.text_color)
        #Add border?
        self.image.blit(text_image, (0, 1))
        self.image.convert_alpha()