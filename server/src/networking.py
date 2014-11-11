from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory
from player import *
from projectile import *
from gamemodeData import *
import base64
import json

class GameServerProtocol(LineReceiver):
    def __init__(self, factory, addr):
        self.factory = factory
        self.addr = addr
        self.name = ""
        self.valid_login = False
    def login(self, name):
        #Validate username with password here
        if name in self.factory.protocols:
            self.factory.data_handler.send_packet(self, "login_fail", "A player with this name is already in the game!")
            self.transport.loseConnection()
            return False
        if name == "_all" or len(name) > 24:
            self.factory.data_handler.send_packet(self, "login_fail", "Illegal name!")
            self.transport.loseConnection()
            return False
        self.name = name
        self.valid_login = True
        self.factory.server.network_data_handler.send_packet(self, "login_succeed")
        self.factory.add_player(self)
        return True
    def lineReceived(self, line):
        self.factory.server.network_data_handler.receive_data(self, line)
    def connectionMade(self):
        self.factory.server.log("Connected to " + self.addr.host)
    def connectionLost(self, reason):
        self.factory.server.log("Lost connection to " + self.addr.host)
        if self.valid_login:
            self.factory.remove_player(self)
    
class GameServerFactory(ServerFactory):
    def __init__(self, server):
        self.server = server
        self.data_handler = server.network_data_handler
        self.protocols = {}
    def buildProtocol(self, addr):
        self.server.log("Received connection from " + addr.host)
        protocol = GameServerProtocol(self, addr)
        return protocol
    def add_player(self, protocol):
        #print("ADDING PLAYER")
        self.protocols[protocol.name] = protocol
        player = PlayerClass(self.server, [0, 0], protocol.name)
        if not self.server.gamemode == "freeplay":
            try:
                player.gamemode_data = gamemodes[self.server.gamemode]["default_player_data"]
            except:
                pass
        self.data_handler.send_packet_all("player_join", protocol.name)
        self.data_handler.send_packet(protocol, "player_list", \
            [player.name for player in self.server.players])
        for player in self.server.players:
            self.data_handler.send_packet(protocol, "player_data_location", player.name, [player.rect.x, player.rect.y])
            self.data_handler.send_packet(protocol, "player_data_movement", player.name, player.movement)
        self.data_handler.send_packet(protocol, "player_data_health", protocol.name, player.health)
        #self.server.network_data_handler.send_packet(protocol, "blocks", self.server.blocks.convert_list())
    def remove_player(self, protocol):
        self.protocols.pop(protocol.name)
        player = self.server.name_to_player(protocol.name)
        self.server.players.remove(player)
        self.data_handler.send_packet_all("player_leave", protocol.name)
    
class DataHandler():
    def __init__(self, server):
        self.server = server
    def receive_data(self, protocol, encoded):
        data = base64.b64decode(encoded)
        packet = json.loads(data)
        self.handle_packet(protocol, packet)
    def send_data(self, protocol, packet):
        data = json.dumps(packet)
        encoded = base64.b64encode(data)
        protocol.sendLine(encoded)
    def handle_packet(self, protocol, packet):
        packet_type = packet["type"]
        if not protocol.valid_login:
            if packet_type == "player_name":
                valid = protocol.login(packet["data"][0])
        else:
            if packet_type == "player_movement_input": #Game handling packets here
                player = self.server.name_to_player(protocol.name)
                player.update_movement_input(packet["data"][0])
            elif packet_type == "respawn":
                player = self.server.name_to_player(protocol.name)
                player.respawn()
            elif packet_type == "click_event":
                button = packet["data"][0]
                location = packet["data"][1]
                player = self.server.name_to_player(protocol.name)
                player.inventory.use_item(button, location)
            elif packet_type == "slot_selected":
                slot = int(packet["data"][0])
                player = self.server.name_to_player(protocol.name)
                player.inventory.update_selected(slot)
            elif packet_type == "launch_projectile":
                player = self.server.name_to_player(protocol.name)
                if player.movement["dead"]:
                    return
                if packet["data"][0][0] - player.rect.x > 0:
                    x_factor = 1
                else:
                    x_factor = -1
                ProjectileClass(self.server, "missile", [30 * x_factor, 1], [player.rect.centerx + 17 * x_factor, player.rect.centery])
            elif packet_type == "get_map":
                location = tuple(packet["data"][0])
                self.send_packet(protocol, "map", location, self.server.maps.get_map(location).convert_list())
            elif packet_type == "player_message":
                self.server.receive_message(packet["data"][0], protocol)
    def send_packet_all(self, type, *data):
        for protocol in self.server.network_factory.protocols.itervalues():
            self.send_packet_base(protocol, type, data)
    def send_packet(self, protocol, type, *data):
        self.send_packet_base(protocol, type, data)
    def send_packet_base(self, protocol, type, data): #Done like this to allow common way of sending packets to one/all protocols
        if self.server.debug:
            print("SENDING PACKET: ", type)
        packet = {"type":type, "data":data}
        self.send_data(protocol, packet)