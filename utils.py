class Toggle():
    def __init__(self, value = True):
        if isinstance(value, bool):
            self.value = value
        else:
            self.value = True
    def toggle(self):
        self.value = not self.value
    def set(self, value):
        if isinstance(value, bool):
            self.value = value
    def get(self):
        return self.value

def string_to_boolean(string):
    if string in ("true", "True"):
        return True
    elif string in ("false", "False"):
        return False
    return None