import pygame
import datetime, sys
from networking import *
from items import *
from terrain import *
from player import *
from colors import *
from identifier import *
from projectile import *

class ServerClass():
    def __init__(self, debug = False):
        self.debug = debug
        pygame.display.set_mode((50,50))
        self.clock = pygame.time.Clock()
        try:
            self.log_file = open("..\\data\\server_log.txt", 'a')
        except:
            self.log_file = open("..\\data\\server_log.txt", 'w')
        self.log("Game Server Started!")
        self.FPS = 60
        self.timer = 0
        self.identifier_generator = IdentifierGeneratorClass(self)
        self.players = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.maps = MapContainerClass(self)
        self.terrain_generator = TerrainEngine(self)
        self.network_data_handler = DataHandler(self)
        self.network_listening_port = None
        self.network_factory = None
    def start_server(self, port = 8007):
        factory = GameServerFactory(self)
        self.network_listening_port = reactor.listenTCP(int(port), factory)
        self.network_factory = factory
        reactor.callLater(1/self.FPS, self.game_loop)
        self.clock.tick(self.FPS)
        reactor.run()
    def game_loop(self):
        self.debug_loop()
        if self.timer == 2:
            self.update_players()
            self.update_projectiles()
            self.timer = 0
        self.timer += 1
        reactor.callLater(1/self.FPS, self.game_loop)
        self.clock.tick(self.FPS)
    def debug_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    PlayerClass(self, [0,0], "Addgame")
                    print("Added")
                elif event.key == pygame.K_2:
                    print([player.name for player in self.players])
                elif event.key == pygame.K_3:
                    self.players.empty()
                    print("Emptied")
                elif event.key == pygame.K_4:
                    print([player.rect for player in self.players])
                elif event.key == pygame.K_5:
                    self.terrain_generator.simple_random_gen()
                elif event.key == pygame.K_6:
                    ProjectileClass(self, "missile", [30,2], [0,0])
                elif event.key == pygame.K_7:
                    for player in self.players:
                        player.take_damage(10, 'magic')
                elif event.key == pygame.K_8:
                    for item in self.maps.maps.iteritems():
                        print(item[1].all)
            elif event.type == pygame.QUIT:
                self.quit()
    def log(self, message, type = "INFO"):
        time = str(datetime.datetime.now())
        time_stamp = '[' + time.split('.')[0] + '] [' + type + ']: '
        log_message = time_stamp + message
        print(log_message)
        self.log_file.write(log_message + '\n')
    def update_players(self):
        for player in self.players:
            player.update()
    def name_to_player(self, name):
        for player in self.players:
            if player.name == name:
                return player
    def update_projectiles(self):
        for projectile in self.projectiles:
            projectile.update()
    def quit(self):
        self.network_listening_port.stopListening()
        reactor.stop()

class MapContainerClass():
    def __init__(self, server):
        self.server = server
        self.maps = {}
        self.map_size_x = 512
        self.map_size_y = 512
        self.clear()
    def clear(self):
        for loc, map in self.maps.iteritems(): #Done like this for possible further expansion
            map.empty()
    def reset(self):
        self.maps = {}
    def loc_to_map(self, location):
        map_x = location[0] >> 9
        map_y = location[1] >> 9
        x = location[0] - (map_x * self.map_size_x)
        y = location[1] - (map_y * self.map_size_y)
        return self.get_map((map_x, map_y)), (x, y) #Returns map and location in map
    def loc_to_map_loc(self, location):
        map_x = location[0] >> 9
        map_y = location[1] >> 9
        x = location[0] - (map_x * self.map_size_x)
        y = location[1] - (map_y * self.map_size_y)
        return (map_x, map_y), (x, y) #Returns map_loc and location "in map"
    def get_map(self, map_loc):
        try:
            return self.maps[map_loc]
        except:
            self.create_map(map_loc)
            return self.maps[map_loc]
    def create_map(self, location):
        self.maps[location] = MapClass(self.server, location)
    def combine(self, map1, map2):
        new_map = MapClass(self.server)
        new_map.all.add(map1.all, map2.all)
        new_map.solid.add(map1.solid, map2.solid)
        new_map.nonsolid.add(map1.nonsolid, map2.nonsolid)
        new_map.damaging.add(map1.damaging, map2.damaging)
        return new_map
    def set_block(self, block):
        map = self.loc_to_map(block.rect.topleft)[0]
        map.map_add_block(block)
    def remove_block(self, data):
        if isinstance(data, BlockClass):
            block = data
            map = self.loc_to_map(block.rect.topleft)[0]
            map.map_remove_block(block)

class MapClass(): #Each Map is a 512 by 512 area
    def __init__(self, server, location = None):
        self.server = server
        self.map_loc = location
        self.all = pygame.sprite.Group()
        self.solid = pygame.sprite.Group()
        self.nonsolid = pygame.sprite.Group()
        self.damaging = pygame.sprite.Group()
    def empty(self, type = "all"):
        if type == "all":
            self.all.empty()
            self.solid.empty()
            self.nonsolid.empty()
            self.damaging.empty()
        elif type == "solid":
            self.solid.empty()
        elif type == "nonsolid":
            self.nonsolid.empty()
        elif type == "damaging":
            self.damaging.empty()
    def convert_list(self):
        list = []
        for block in self.all:
            block_dict = {"location":[block.rect.x, block.rect.y], "name":block.block_name}
            list.append(block_dict)
        return list
    def map_add_block(self, block):
        self.all.add(block)
        if block.solidity == "solid":
            self.solid.add(block)
        else:
            self.nonsolid.add(block)
        if block.damage != None:
            self.damaging.add(block)
        self.server.network_data_handler.send_packet_all("map", self.map_loc, self.convert_list())
    def map_remove_block(self, block):
        self.all.remove(block)
        if block.solidity == "solid":
            self.solid.remove(block)
        else:
            self.nonsolid.remove(block)
        if block.damage != None:
            self.damaging.remove(block)
        self.server.network_data_handler.send_packet_all("map", self.map_loc, self.convert_list())

if __name__ == "__main__":
    pygame.init()
    server = ServerClass()
    try:
        server.start_server(sys.argv[1])
    except:
        server.start_server(8007)