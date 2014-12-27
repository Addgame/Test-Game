from colors import *
from utils import *
from .base import *

class Button(GuiObject):
    def __init__(self, text = "", **params):
        self.text = text
        self.text_color = params.get("text_color", BLACK)
        self.font = params.get("font", pygame.font.Font("..\\data\\fonts\\corbelb.ttf", 20))
        if not params.get("size", None):
            size = self.font.size("a" * len(text))
            params["size"] = (size[0] + 10, size[1] + 10)
        self.bg_color = params.get("bg_color", (191, 161, 121))
        self.border_color = params.get("border_color", (249, 205, 87))
        GuiObject.__init__(self, **params)
        self.calls = []
        #self.create_bg_image()
        self.update_image()
    def update_image(self):
        bg_image = pygame.Surface((self.rect.width + 4, self.rect.height + 4))
        bg_image.fill(BLACK)
        bg_image.fill(self.border_color, pygame.Rect(2, 2, self.rect.width, self.rect.height))
        bg_image.fill(self.bg_color, pygame.Rect(4, 4, self.rect.width - 4, self.rect.height - 4))
        self.image = pygame.Surface(bg_image.get_rect().size, pygame.SRCALPHA)
        self.image.blit(bg_image, (0,0))
        self.image.blit(self.font.render(self.text, True, self.text_color), ((self.image.get_width() / 2) - (self.font.size(self.text)[0] / 2), 8))
    def click(self, pos):
        self.bg_color = (145, 112, 75)
        self.update_image()
    def release(self, pos):
        self.bg_color = (191, 161, 121)
        self.update_image()
        if self.rect.collidepoint(pos):
            self.activate()
    def attach(self, func, *args, **params):
        self.calls.append(Call(func, *args, **params))
    def activate(self):
        for call in self.calls:
            call.call()

class CheckBox(GuiObject):
    def __init__(self, checked = False, **params):
        pass