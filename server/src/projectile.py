import pygame
from projectileData import *

class ProjectileClass(pygame.sprite.Sprite):
    def __init__(self, server, type, velocity, location):
        pygame.sprite.Sprite.__init__(self)
        self.server = server
        self.identifier = self.server.identifier_generator.generate()
        self.type = type
        self.velocity = velocity
        self.rect = pygame.Rect(location, projectile_data[type]["size"])
        self.server.projectiles.add(self)
        self.server.network_data_handler.send_packet_all("new_projectile", self.identifier, self.convert_dict())
    def update(self):
        temp_rect = self.rect.center
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if self.rect.x > 1430 or self.rect.x < -64 or self.rect.y > 832 or self.rect.y < -64:
            self.delete()
            return
        player_collisions = pygame.sprite.spritecollide(self, self.server.players, False)
        for player in player_collisions:
            player.take_damage(projectile_data[self.type]["damage"], self.type)
        block_collisions = pygame.sprite.spritecollide(self, self.server.blocks.solid, False)
        for block in block_collisions:
            pass
        if player_collisions != []:
            self.delete()
            return
        elif block_collisions != []:
            self.delete()
            return
        if self.rect.center != temp_rect:
            self.server.network_data_handler.send_packet_all("projectile_data_location", self.identifier, [self.rect.x, self.rect.y])
    def convert_dict(self):
        return {"location": [self.rect.x, self.rect.y], "type": self.type, "velocity": self.velocity}
    def delete(self):
        self.kill()
        self.server.network_data_handler.send_packet_all("remove_projectile", self.identifier)