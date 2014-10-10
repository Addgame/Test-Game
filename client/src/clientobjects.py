import pygame, random

class ClientMapGroup():
    def __init__(self, client):
        self.client = client
        self.maps = {}
        self.waiting_maps = []
    def loc_to_map(self, location):
        map_x = location[0] >> 9
        map_y = location[1] >> 9
        x = location[0] - (map_x * self.map_size_x)
        y = location[1] - (map_y * self.map_size_y)
        try:
            return self.maps[(map_x, map_y)], (x, y) #Returns map and location in map
        except:
            self.get_map((map_x, map_y))
            return self.maps[(map_x, map_y)], (x, y)
    def loc_to_map_loc(self, location):
        map_x = location[0] >> 9
        map_y = location[1] >> 9
        x = location[0] - (map_x * self.map_size_x)
        y = location[1] - (map_y * self.map_size_y)
        return (map_x, map_y), (x, y) #Returns map_loc and location "in map"
    def get_map(self, map_loc):
        if map_loc not in self.waiting_maps:
            try:
                return self.maps[map_loc]
            except:
                self.send_get_map_packet(map_loc)
                self.waiting_maps.append(map_loc)
                return None
    def send_get_map_packet(self, location):
        self.client.network_data_handler.send_packet("get_map", location)
    def receive_map(self, map_loc, list):
        map = ClientMapClass(self.client, map_loc, list)
        self.maps[map_loc] = map
        if map_loc in self.waiting_maps:
            self.waiting_maps.remove(map_loc)
    def create_map(self, location, map_list):
        self.maps[location] = ClientMapClass(location, map_list)
    def set_block(self, block):
        map = self.loc_to_map(block.rect.topleft)[0]
        map.map_add_block(block)
    def remove_block(self, data):
        if isinstance(data, BlockClass):
            block = data
            map = self.loc_to_map(block.rect.topleft)[0]
            map.map_remove_block(block)

class ClientMapClass():
    def __init__(self, client, location, list = None):
        self.client = client
        self.map_loc = location
        self.draw_loc = [self.map_loc[0] << 9, self.map_loc[1] << 9]
        self.blocks = pygame.sprite.Group()
        self.image = pygame.surface.Surface((512, 512), pygame.SRCALPHA)
        if list:
            self.from_list(list)
    def from_list(self, list):
        for item in list:
            block = ClientBlockClass(self.client, item["name"], item["location"])
            self.map_add_block(block)
        self.create_image()
    def create_image(self):
        self.image = pygame.surface.Surface((512, 512), pygame.SRCALPHA)
        #self.image.fill((255, 255, 255, 255))
        self.image.fill((random.randint(0,255), random.randint(0,255), random.randint(0,255), 127))
        for block in self.blocks:
            self.image.blit(block.image, [block.location[0] - self.draw_loc[0], block.location[1] - self.draw_loc[1]])
        self.image.convert_alpha()
    def map_add_block(self, block):
        self.blocks.add(block)
        self.create_image()
    def map_remove_block(self, block):
        self.blocks.remove(block)
        self.create_image()

class ClientBlockClass(pygame.sprite.Sprite):
    def __init__(self, client, name, location):
        pygame.sprite.Sprite.__init__(self)
        self.client = client
        self.name = name
        self.location = location
        self.image = self.client.graphics.block_textures[self.name]