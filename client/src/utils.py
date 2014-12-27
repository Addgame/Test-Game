import win32clipboard as cb

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

class Call():
    """
    Represents a function to be called later
    """
    def __init__(self, func, *args, **params):
        self.func = func
        self.args = args
        self.params = params
    def call(self):
        self.func(*self.args, **self.params)

def string_to_boolean(string):
    if string in ("true", "True"):
        return True
    elif string in ("false", "False"):
        return False
    return None

def get_clipboard():
    cb.OpenClipboard()
    data = cb.GetClipboardData()
    cb.CloseClipboard()

def set_clipboard(data):
    cb.OpenClipboard()
    cb.SetClipboardText(data)
    cb.CloseClipboard()