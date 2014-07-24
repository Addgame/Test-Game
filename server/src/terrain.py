import random
from items import *

class TerrainEngine():
    def __init__(self, server):
        self.server = server
    def simple_random_gen(self):
        self.server.blocks.reset()
        for x in range(42):
            y = random.randint(4,23) * 32
            type = random.choice(["dirt","grass"])
            block = BaseItemClass.BlockClass(type, self.server.blocks, [x * 32,y])
            block.group(False)
        self.server.log("Simple Random Generation Performed")
        self.server.network_data_handler.send_packet_all("blocks", self.server.blocks.convert_list())
        