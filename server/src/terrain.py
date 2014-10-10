import random
from items import *

class TerrainEngine():
    def __init__(self, server):
        self.server = server
        self.current_generation = self.simple_random_gen
    def simple_random_gen(self):
        self.server.maps.reset()
        for x in range(42):
            y = random.randint(4,23) * 32
            type = random.choice(["dirt","grass"])
            block = BlockClass(self.server, type, [x * 32,y])
        self.server.log("Simple Random Generation Performed")
        #self.server.network_data_handler.send_packet_all("blocks", self.server.blocks.convert_list())