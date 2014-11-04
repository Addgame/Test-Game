import random
from items import *

class TerrainEngine():
    def __init__(self, server):
        self.server = server
        self.current_generation = self.simple_random_gen
    def simple_random_gen(self):
        self.server.maps.clear()
        for x in range(42):
            y = random.randint(4,23) * 32
            type = random.choice(["dirt","grass"])
            block = BlockClass(self.server, type, [x * 32,y])
        self.server.log("Simple Random Generation Performed")
    def random_gen(self):
        self.server.maps.clear()
        for x in range(42):
            y = random.randint(4,23)
            if y < 10:
                type = random.choice(["dirt","grass"])
            elif y > 10:
                type = random.choice(["dirt","stone"])
            else:
                type = "test_block"
            block = BlockClass(self.server, type, [x * 32,y * 32])
        self.server.log("Random Generation Performed")