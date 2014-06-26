import pygame
from blockData import *

class BaseItemClass():
    class ItemClass():
        pass
    class BlockClass(pygame.sprite.Sprite):
        def __init__(self, name, location, blocks):
            pygame.sprite.Sprite.__init__(self)
            self.server = blocks.server
            self.solidity = block_data[name]["solidity"]
            self.name = name
            self.rect = pygame.Rect([location[0], location[1]], block_data[name]["size"])
            self.active = False
            self.break_progress = 0
            self.grouped = False
            self.groupings = [blocks.all]
            if self.solidity == "solid":
                self.groupings.append(blocks.solid)
            elif self.solidity == "nonsolid":
                self.groupings.append(blocks.nonsolid)
            for extraInfo in block_data[name]["extra"]:
                if extraInfo == 'damage':
                    self.groupings.append(blocks.damaging)
                    self.damage_rect = pygame.Rect(location[0]-2, location[1]-2, self.rect.width + 4, self.rect.height + 4)
                elif extraInfo == 'active':                
                    self.active = True
        def __str__(self):
            msg = self.name + " block of type " + self.type + " with groups of " + self.groupings
            return msg
        def group(self, update = True):
            if not(self.grouped):
                for group in self.groupings:
                    group.add(self)
                self.grouped = True
                if update:
                    self.send_block_update()
        def ungroup(self, update = True):
            if self.grouped:
                self.kill()
                if update:
                    self.send_block_update()
        def send_block_update(self):
            self.server.network_data_handler.send_packet_all("blocks", self.server.blocks.convert_list())
        def place(self, player):
            self.rect.x = (int(player.cursor.rect.centerx / self.rect.width) * self.rect.width)
            if self.rect.x < 0:
                self.rect.x -= 1
            self.rect.y = (int(player.cursor.rect.centery / self.rect.height) * self.rect.height)
            if self.rect.y < 0:
                self.rect.y -= 1
            self.group()