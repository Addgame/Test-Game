import pygame
from colors import *
from clientobjects import *

class GraphicsEngineClass():
    def __init__(self, client, screen, size, texture_directory = "default"):
        self.client = client
        self.texture_dir = texture_directory
        self.load_all_textures()
        self.load_player_skins("_all")
        self.fonts = { \
            "corbel-15": pygame.font.Font("..\\data\\fonts\\corbel.ttf", 15), \
            "corbelb-15": pygame.font.Font("..\\data\\fonts\\corbelb.ttf", 15), \
            "corbel-25": pygame.font.Font("..\\data\\fonts\\corbel.ttf", 25), \
            }
        if screen != None:
            size = screen.get_size()
        self.create_display(size)
        self.client.clock.tick(float(self.client.options["fps"]))
    def create_display(self, size, flags = 0):
        self.screen = pygame.display.set_mode(size, flags)
        pygame.display.set_caption("Dungeon Derps v." + self.client.version)
        pygame.display.set_icon(pygame.image.load("..\\data\\textures\\icon.png"))
        self.death_screen = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.death_screen.fill(REDFADE)
        self.connection_lost_screen = self.fonts["corbel-25"].render("Lost Connection to Server!", True, WHITE)
        self.sky_image = pygame.transform.scale(pygame.image.load("..\\data\\textures\\packs\\" + self.texture_dir + "\\sky.png"), self.screen.get_size())
        try:
            self.client.message_group.update_display = True
            self.client.message_group.update_location = True
            self.client.chat_box.update_location()
        except: #MessageGroup instance not created yet
            pass
    def draw_screen(self):
        if self.client.game_state == "ingame":
            self.draw_game_screen()
        elif self.client.game_state == "connection_lost":
            self.screen.fill(BLACK)
            self.screen.blit(self.connection_lost_screen, self.connection_lost_screen.get_rect( \
                center=(self.screen.get_rect().centerx, self.screen.get_rect().centery-10)))
        if self.client.show_fps:
            self.screen.blit(self.fonts["corbel-15"].render("FPS: {:.1f}".format(self.client.clock.get_fps()), True, RED), [self.screen.get_width() - 63,0])
        pygame.display.update()
        self.client.clock.tick()
    def draw_game_screen(self):
        self.draw_background()
        self.draw_blocks()
        self.draw_players()
        self.draw_projectiles()
        self.draw_messages()
        self.draw_chat_box()
        if self.client.show_hud:
            self.draw_hud()
        self.draw_cursor()
##        if self.client.show_fps:
##            self.screen.blit(self.fonts["corbel-15"].render("FPS: {:.1f}".format(self.client.clock.get_fps()), True, BLUE), [self.screen.get_width() - 63,0])
##        pygame.display.update()
##        self.client.clock.tick()#float(self.client.options["fps"]))
    def draw_blocks(self):
        for x in range(self.client.player.current_map[0] - 2, self.client.player.current_map[0] + 3):
            for y in range(self.client.player.current_map[1] - 1, self.client.player.current_map[1] + 2):
                map = self.client.maps.get_map((x,y))
                if map:
                    self.screen.blit(map.image, [map.draw_loc[0] - self.client.player.rect.x + (self.screen.get_rect().centerx - 15), \
                        map.draw_loc[1] - self.client.player.rect.y + (self.screen.get_rect().centery - 15)])
    def draw_players(self):
        self.update_player_skins()
        for name in self.client.players.names:
            if name != self.client.player_name:
                player = self.client.players.name_to_player(name)
                self.screen.blit(player.current_img, [player.rect.x - self.client.player.rect.x + (self.screen.get_rect().centerx - 15), \
                    player.rect.y - self.client.player.rect.y + (self.screen.get_rect().centery - 15)])
        if self.client.player:
            #self.screen.blit(self.client.player.current_img, self.client.player.location)
            self.screen.blit(self.client.player.current_img, [self.screen.get_rect().centerx - 15, self.screen.get_rect().centery - 15])
    def draw_background(self):
        #self.screen.fill(WHITE)
        self.screen.blit(self.sky_image, [0,0])
    def draw_messages(self):
        self.client.message_group.update()
        self.client.message_group.draw()
    def draw_chat_box(self):
        self.client.chat_box.draw()
    def draw_cursor(self):
        self.screen.blit(self.client.cursor.image, self.client.cursor.rect)
    def draw_hud(self):
        location = [1, 1]
        hearts = self.client.player.health / 20.0
        while hearts > 0:
            if hearts > .5:
                self.screen.blit(self.hud_textures["heart"], location)
                location[0] += self.hud_textures["heart"].get_width() + 1
            else:
                self.screen.blit(self.hud_textures["hearthalf"], location)
                location[0] += self.hud_textures["hearthalf"].get_width() + 1
            hearts -= 1
        if self.client.show_list:
            for slot in range(len(self.client.players.names)):
                self.screen.blit(self.hud_textures["listslot"],\
                    [(self.screen.get_width() / 2) - self.hud_textures["listslot"].get_width() / 2, (slot * 22) + 4])
                self.screen.blit(self.fonts["corbelb-15"].render(self.client.players.names[slot], True, self.client.players.names_color[self.client.players.names[slot]]), \
                    [(self.screen.get_width() / 2) - self.hud_textures["listslot"].get_width() / 2 + 4, (slot * 22) + 8])
        self.client.player.inventory.draw()
        if self.client.player.movement["dead"] == True:
            self.screen.blit(self.death_screen, [0,0])
    def draw_projectiles(self):
        for identifier, data in self.client.projectiles.items():
            image = self.projectile_textures[data["type"]]
            if data["velocity"][0] < 0:
                image = pygame.transform.flip(image, True, False)
            #self.screen.blit(image, data["location"])
            self.screen.blit(image, [data["location"][0] - self.client.player.rect.x + (self.screen.get_rect().centerx - 15), \
                data["location"][1] - self.client.player.rect.y + (self.screen.get_rect().centery - 15)])
    def load_player_skins(self, name):
        if name == "_all":
            for player in self.client.players:
                player.load_images()
        else:
            self.client.players.name_to_player(name).load_images()
    def update_player_skins(self):
        for player in self.client.players:
            player.update_image()
    def set_texture_directory(self, directory):
        self.texture_dir = directory
        self.load_all_textures()
    def load_all_textures(self):
        self.load_projectile_textures()
        self.load_hud_textures()
        self.load_block_textures()
        self.load_item_textures()
    def load_block_textures(self):
        self.block_textures = {"dirt": None, "dirt_wall": None, "grass": None, "spike": None, "stone": None, "test_block": None}
        for key in self.block_textures:
            try:
                self.block_textures[key] = pygame.image.load("..\\data\\textures\\packs\\" + self.texture_dir + "\\blocks\\" + key + ".png")
            except:
                self.block_textures[key] = pygame.image.load("..\\data\\textures\\packs\\default\\blocks\\" + key + ".png")
    def get_cursor_textures(self):
        texture = pygame.image.load("..\\data\\textures\\packs\\" + self.texture_dir + "\\cursor\\cursor.png")
        return texture
    def load_hud_textures(self):
        self.hud_textures = {"heart": None, "hearthalf": None, "inventoryslot": None, "slothighlight": None, "hotbarslot": None, "listslot": None}
        for key in self.hud_textures:
            try:
                self.hud_textures[key] = pygame.image.load("..\\data\\textures\\packs\\" + self.texture_dir + "\\hud\\" + key + ".png")
            except:
                self.hud_textures[key] = pygame.image.load("..\\data\\textures\\packs\\default\\hud\\" + key + ".png")
    def load_projectile_textures(self):
        self.projectile_textures = {"missile": None}
        for key in self.projectile_textures:
            try:
                self.projectile_textures[key] = pygame.image.load("..\\data\\textures\\packs\\" + self.texture_dir + "\\projectiles\\" + key + ".png")
            except:
                self.projectile_textures[key] = pygame.image.load("..\\data\\textures\\packs\\default\\projectiles\\" + key + ".png")
    def load_item_textures(self):
        self.item_textures = {"wand_gold": None}
        for key in self.item_textures:
            try:
                self.item_textures[key] = pygame.image.load("..\\data\\textures\\packs\\" + self.texture_dir + "\\items\\" + key + ".png")
            except:
                self.item_textures[key] = pygame.image.load("..\\data\\textures\\packs\\default\\items\\" + key + ".png")