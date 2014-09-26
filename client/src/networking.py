from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
import base64
import json
from client import MessageClass
from colors import *

class GameClientProtocol(LineReceiver):
    def __init__(self, factory):
        self.factory = factory
    def lineReceived(self, line):
        self.factory.client.network_data_handler.receive_data(line)
    def connectionMade(self):
        self.factory.client.network_data_handler.send_packet("player_name", self.factory.client.player_name)

class GameClientFactory(ClientFactory):
    def __init__(self, client):
        self.client = client
        self.protocol = GameClientProtocol(self)
    def startedConnecting(self, connector):
        self.client.log("Connecting to server!")
    def buildProtocol(self, addr):
        self.client.log("Connected to server: " + addr.host + ":" + str(addr.port))
        self.client.connected = True
        return self.protocol
    def clientConnectionFailed(self, connector, reason):
        self.client.log("Could not connect to server!", "ERROR")
        if self.client.debug:
            self.client.log("REASON: " + str(reason), "DEBUG")
    def clientConnectionLost(self, connector, reason):
        self.client.log("Disconnected from server!")
        if self.client.debug:
            self.client.log("REASON: " + str(reason), "DEBUG")
        self.client.connected = False
        self.client.game_state = "connection_lost"

class DataHandler():
    def __init__(self, client):
        self.client = client
    def receive_data(self, encoded):
        data = base64.b64decode(encoded)
        packet = json.loads(data)
        self.handle_packet(packet)
    def send_data(self, packet):
        data = json.dumps(packet)
        encoded = base64.b64encode(data)
        self.client.network_protocol.sendLine(encoded)
    def handle_packet(self, packet):
        if self.client.debug:
            self.client.log("RECEIVED PACKET: " + str(packet))
        packet_type = packet["type"]
        if self.client.game_state == "login":
            if packet_type == "login_succeed":
                self.client.game_state = "ingame"
            elif packet_type == "login_fail":
                self.client.log("Login Failed. Reason: " + packet["data"][0], "ERROR")
                self.client.network_protocol.transport.loseConnection()
        elif self.client.game_state == "ingame":
            if packet_type == "player_list":
                for name in packet["data"][0]:
                    if name not in self.client.players.names:
                        self.client.players.add_player(name)
                if self.client.debug:
                    print("RECEIVED PLAYERS")
            elif packet_type == "player_data_location":
                name = packet["data"][0]
                self.client.players.name_to_player(name).location = packet["data"][1]
                if self.client.debug:
                    print("RECEIVED PLAYER {} LOCATION".format(name))
            elif packet_type == "player_data_movement":
                name = packet["data"][0]
                self.client.players.name_to_player(name).movement = packet["data"][1]
            elif packet_type == "player_data_health":
                name = packet["data"][0]
                self.client.players.name_to_player(name).health = packet["data"][1]
            elif packet_type == "new_projectile":
                self.client.projectiles[packet["data"][0]] = packet["data"][1]
            elif packet_type == "projectile_data":
                for key in packet["data"][1]:
                    self.client.projectiles[packet["data"][0]][key] = packet["data"][1][key]
            elif packet_type == "projectile_data_location":
                self.client.projectiles[packet["data"][0]]["location"] = packet["data"][1]
            elif packet_type == "projectile_data_velocity":
                self.client.projectiles[packet["data"][0]]["velocity"] = packet["data"][1]
            elif packet_type == "remove_projectile":
                self.client.projectiles.pop(packet["data"][0])
            elif packet_type == "blocks":
                self.client.blocks = packet["data"][0]
                if self.client.debug:
                    print("RECEIVED BLOCKS")
            elif packet_type == "player_join":
                name = packet["data"][0]
                self.client.players.add_player(name)
                message = MessageClass("{} has joined the server".format(name), color = BLUE)
                self.client.message_group.add_message(message)
            elif packet_type == "player_leave":
                name = packet["data"][0]
                self.client.players.remove_player(name)
                message = MessageClass("{} has left the server".format(name), color = RED)
                self.client.message_group.add_message(message)
            elif packet_type == "death":
                if self.client.debug:
                    print("RECEIVED DEATH")
                #self.client.players[self.client.player_name]["movement"]["dead"] = True
                self.client.sound.sounds["death"].play()
            elif packet_type == "chat_message":
                message = MessageClass(packet["data"][0])
                self.client.message_group.add_message(message)
    def send_packet(self, type, *data):
        if self.client.debug:
            print("SENDING PACKET: ", type)
        packet = {"type":type, "data":data}
        self.send_data(packet)