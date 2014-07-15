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
        self.blocks = BlockHoldingClass(self)
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

class BlockHoldingClass():
    def __init__(self, server):
        self.server = server
        self.reset()
    def reset(self):
        self.all = pygame.sprite.Group()
        self.solid = pygame.sprite.Group()
        self.nonsolid = pygame.sprite.Group()
        self.damaging = pygame.sprite.Group()
    def convert_list(self):
        list = []
        for block in self.all:
            block_dict = {"location":[block.rect.x, block.rect.y], "name":block.name}
            list.append(block_dict)
        return list

if __name__ == "__main__":
    pygame.init()
    server = ServerClass()
    try:
        server.start_server(sys.argv[1])
    except:
        server.start_server(8007)