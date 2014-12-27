from gui.input import *
from gui.button import *

class LoginMenu():
    def __init__(self, container, username = "", password = ""):
        def print_ln(value):
            print(value)
        username_field = InputBox(username, max_length = 24, location = [850, 300], container = container, focused = True)
        password_field = PasswordInputBox(password, location = [850, 350], container = container)
        login_btn = Button("Log In", location = [930, 400], container = container)
        login_btn.attach(print_ln, "LOG IN")
        quit_btn = Button("Quit", location = [942, 440], container = container)
        quit_btn.attach(print_ln, "QUIT")

class MainMenu():
    def __init__(self):
        play_btn = Button("Play", location = [])
        options_btn = Button("Options", location = [])
        quit_btn = Button("Quit", location = [])