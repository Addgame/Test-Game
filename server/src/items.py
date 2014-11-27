import pygame, math
from projectile import *
from itemData import *

class BaseItemClass(pygame.sprite.Sprite):
    def __init__(self, server, type, count, internal_name, display_name = None):
        pygame.sprite.Sprite.__init__(self)
        self.server = server
        if display_name == None:
            display_name = internal_name
        self.internal_name = internal_name
        self.display_name = display_name
        self.type = type #block, projectile, NONE
        self.count = count
    def convert_dict(self):
        return {"type": self.type, "count": self.count,"internal_name": self.internal_name, "display_name": self.display_name}
    def reduce_count(self, number = 1):
        if type != "NONE":
            self.count -= number
            return True
        return False
    #Add inventory based common item methods

class BlockItemClass(BaseItemClass):
    def __init__(self, server, count, internal_name, display_name = None):
        BaseItemClass.__init__(self, server, "block", count, internal_name, display_name)
    def place(self, location):
        x_factor = int(math.log(block_data[self.internal_name]["size"][0], 2))
        y_factor = int(math.log(block_data[self.internal_name]["size"][1], 2))
        location[0] = location[0] >> x_factor << x_factor
        location[1] = location[1] >> y_factor << y_factor
        block = BlockClass(self.server, self.internal_name, location)
        return block

class ProjectileItemClass(BaseItemClass):
    def __init__(self, server, count, internal_name, display_name = None):
        BaseItemClass.__init__(self, server, "projectile", count, internal_name, display_name)
    def launch(self, location, velocity):
        projectile = ProjectileClass(self.server, self.internal_name, location, velocity)
        return projectile

class NormalItemClass(BaseItemClass):
    def __init__(self, server, count, internal_name, display_name = None):
        BaseItemClass.__init__(self, server, "normal", count, internal_name, display_name)

class BlockClass(pygame.sprite.Sprite):
    def __init__(self, server, name, location):
        pygame.sprite.Sprite.__init__(self)
        self.server = server
        self.block_name = name
        self.solidity = block_data[self.block_name]["solidity"]
        self.rect = pygame.Rect(location, block_data[self.block_name]["size"])
        self.damage = block_data[self.block_name]["damage"]
        if self.damage != None:
            self.damage_rect = pygame.Rect(self.rect.x - 2, self.rect.y - 2, self.rect.width + 4, self.rect.height + 4)
        self.break_progress = 0
        self.placed = self.server.maps.set_block(self)
    def destroy(self):
        self.server.maps.remove_block(self)