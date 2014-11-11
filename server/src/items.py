import pygame

from blockData import *

class BaseItemClass(pygame.sprite.Sprite):
    def __init__(self, server, type, count, internal_name, display_name = None):
        pygame.sprite.Sprite.__init__(self)
        self.server = server
        if display_name == None:
            display_name = internal_name
        self.iternal_name = internal_name
        self.display_name = display_name
        self.type = type #Ex: block, NONE
        self.count = count
    def convert_dict(self):
        return {"type": self.type, "count": self.count,"internal_name": self.iternal_name, "display_name": self.display_name}
    def reduce_count(self, number = 1):
        if type != "NONE":
            self.count -= number
            return True
        return False
    #Add inventory based common item methods

class BlockItemClass(BaseItemClass):
    def __init__(self, server, count, internal_name, display_name = None):
        BaseItemClass.__init__(self, server, "block", count, internal_name, display_name)
        self.internal_name = internal_name
    def place(self, location):
        location[0] = location[0] >> 5 << 5
        location[1] = location[1] >> 5 << 5
        block = BlockClass(self.server, self.internal_name, location)
        return block

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
        self.placed = self.server.maps.set_block(self)
