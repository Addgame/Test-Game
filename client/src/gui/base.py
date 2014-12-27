import pygame

class GuiObject():
    def __init__(self, **params): #container, location, size):
        self.container = params.get("container", None)
        self.rect = pygame.Rect(params.get("location", [0,0]), params.get("size", (0,0)))
        self.focused = params.get("focused", False)
        self.focusable = params.get("focusable", False)
        if self.container:
            self.container.add(self, self.focused)
    def gain_focus(self):
        pass
    def lose_focus(self):
        pass
    def handle_event(self, event):
        pass
    def click(self, pos):
        pass
    def release(self, pos):
        pass

class Container():
    def __init__(self, screen, objects = []):
        self.screen = screen
        self.objects = objects
        self.focused_object = None
        self.pressed = []
    def draw(self):
        for obj in self.objects:
            self.screen.blit(obj.image, obj.rect)
    def add(self, obj, focus = False):
        self.objects.append(obj)
        if focus:
            self.set_focus(obj)
    def remove(self, obj):
        self.objects.remove(obj)
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            used = False
            for obj in self.objects:
                if obj.rect.collidepoint(pygame.mouse.get_pos()):
                    obj.click(pygame.mouse.get_pos())
                    self.pressed.append(obj)
                    used = True
            if not used:
                self.set_focus()
        elif event.type == pygame.MOUSEBUTTONUP:
            for obj in self.pressed:
                obj.release(pygame.mouse.get_pos())
                self.pressed.remove(obj)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            if self.focused_object:
                index = self.objects.index(self.focused_object) + 1
            else:
                index = 0
            if index >= len(self.objects):
                index = 0
            self.set_focus(self.objects[index])
        else:
            if self.focused_object:
                self.focused_object.handle_event(event)
    def set_focus(self, obj = None):
        if self.focused_object:
            self.focused_object.lose_focus()
            self.focused_object.focused = False
            self.focused_object = None
        if obj and obj.focusable:
            self.focused_object = obj
            obj.focused = True
            obj.gain_focus()