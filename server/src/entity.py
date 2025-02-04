import pygame
#from server import MapClass

class EntityClass(pygame.sprite.Sprite):
    def __init__(self, server):
        from server import MapClass
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.rect.Rect(0,0,1,1) #All subclasses must have rect attribute
        self.server = server
        self.map_class = MapClass
    def check_collisions(self, type):
        left = self.rect.left >> 9
        right = self.rect.right >> 9
        top = self.rect.top >> 9
        bottom = self.rect.bottom >> 9
        #map = MapClass(self.server)
        map = self.map_class(self.server)
        for x in range(left, right + 1):
            for y in range(top, bottom + 1):
                map = self.server.maps.combine(map, self.server.maps.get_map((x, y)))
        if type == "all":
            return pygame.sprite.spritecollide(self, map.all, False)
        elif type == "solid":
            return pygame.sprite.spritecollide(self, map.solid, False)
        elif type == "nonsolid":
            return pygame.sprite.spritecollide(self, map.nonsolid, False)
        elif type == "damaging":
            return pygame.sprite.spritecollide(self, map.damaging, False)
        elif type == "damaging_rect":
            collisions = []
            for dblock in map.damaging:
                if dblock.damage_rect.colliderect(self.rect):
                    collisions.append(dblock)
            return collisions