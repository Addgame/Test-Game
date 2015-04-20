import string
import random

class IdentifierGeneratorClass():
    def __init__(self):
        self.used_identifiers = []
        self.characters = string.ascii_uppercase + string.digits
    def generate(self):
        while True:
            identifier = "".join(random.choice(self.characters) for _ in range(5)) #Generates random 6-character identifier
            if identifier not in self.used_identifiers:
                break
        self.used_identifiers.append(identifier)
        return identifier
    def release(identifier):
        try:
            self.used_identifiers.remove(identifier)
            return True
        except:
            return False