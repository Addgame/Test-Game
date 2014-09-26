import pygame
from colors import *
from clientobjects import *

class GraphicsEngineClass():
    def __init__(self, client, screen, texture_directory = "default"):
        self.client = client
        self.texture_dir = texture_directory
        self.load_projectile_textures()
        self.load_hud_textures()
        self.load_block_textures()
        self.load_player_skins("_all")
        self.fonts = { \
            "corbel-15": pygame.font.Font(pygame.font.match_font("corbel"), 15), \
            "corbel-25": pygame.font.Font(pygame.font.match_font("corbel"), 25), \
            }
        if screen != None:
            size = screen.get_size()
        else:
            size = [1366,768]
        self.create_display(size)
        self.client.clock.tick(float(self.client.options["fps"]))
    def create_display(self, size, flags = 0):
        self.screen = pygame.display.set_mode(size, flags)
        pygame.display.set_caption("My Game v.0.0.4")
        pygame.display.set_icon(pygame.image.load("..\\data\\textures\\icon.png"))
        self.alpha_screen = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.death_screen = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.death_screen.fill(REDFADE)
        self.connection_lost_text = self.fonts["corbel-25"].render("Lost Connection to Server!", True, WHITE)
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
            self.screen.blit(self.connection_lost_text, self.connection_lost_text.get_rect( \
                center=(self.screen.get_rect().centerx, self.screen.get_rect().centery-10)))
            pygame.display.update()
            self.client.clock.tick()#float(self.client.options["fps"]))
    def draw_game_screen(self):
        self.draw_background()
        self.draw_blocks()
        self.draw_players()
        self.draw_projectiles()
        self.draw_messages()
        self.draw_chat_box()
        self.draw_hud()
        self.draw_cursor()
        pygame.display.update()
        self.client.clock.tick()#float(self.client.options["fps"]))
    def draw_blocks(self):
        for block in self.client.blocks:
            self.screen.blit(self.block_textures[block["name"]], block["location"])
    def draw_players(self):
        self.update_player_skins()
        for name in self.client.players.names:
            if name != self.client.player_name:
                player = self.client.players.name_to_player(name)
                self.screen.blit(player.current_img, player.location)
        if self.client.player:
            self.screen.blit(self.client.player.current_img, self.client.player.location)
    def draw_background(self):
        self.screen.fill(WHITE)
    def draw_messages(self):
        self.client.message_group.update()
        self.client.message_group.draw()
    def draw_chat_box(self):
        self.client.chat_box.draw()
    def draw_cursor(self):
        self.client.cursor.draw()
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
        if self.client.player.movement["dead"] == True:
            self.screen.blit(self.death_screen, [0,0])
    def draw_projectiles(self):
        for identifier, data in self.client.projectiles.items():
            image = self.projectile_textures[data["type"]]
            if data["velocity"][0] < 0:
                image = pygame.transform.flip(image, True, False)
            self.screen.blit(image, data["location"])
    def load_player_skins(self, name):
        if name == "_all":
            for player in self.client.players:
                player.load_images()
        else:
            self.client.players.name_to_player(name).load_images()
    def update_player_skins(self):
        for player in self.client.players:
            player.update_image()
    def load_block_textures(self):
        self.block_textures = {"dirt": None, "grass": None, "spike": None, "stone": None, "test_block": None}
        for key in self.block_textures:
            try:
                self.block_textures[key] = pygame.image.load("..\\data\\textures\\packs\\" + self.texture_dir + "\\blocks\\" + key + ".png")
            except:
                self.block_textures[key] = pygame.image.load("..\\data\\textures\\packs\\default\\blocks\\" + key + ".png")
    def get_cursor_textures(self):
        texture = pygame.image.load("..\\data\\textures\\packs\\" + self.texture_dir + "\\cursor\\cursor.png")
        return texture
    def load_hud_textures(self):
        self.hud_textures = {"heart": None, "hearthalf": None}
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