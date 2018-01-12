import base64, json
from gui.input import *
from gui.button import *
from gui.text import *
from colors import *
import pygame

from utils import get_b64_name


class LoginMenu:
    def __init__(self, container, username="", password=""):
        username_field = InputBox(username, max_length=24, location=[503, 350], container=container, focused=True)
        password_field = PasswordInputBox(password, max_length=24, location=[503, 400], container=container)
        login_btn = Button("Log In", location=[583, 450], container=container)
        login_btn.attach(login, username_field, password_field)
        quit_btn = Button("Quit", location=[594, 490], container=container)
        quit_btn.attach(quit)
        # random_text = Text("RANDOM TEXT", location = [900, 500], container = container, text_color = BLUE)


class MainMenu:
    def __init__(self, container):
        play_btn = Button("Play", location=[605, 285], font_size=30, container=container)
        play_btn.attach(play)
        options_btn = Button("Options", location=[583, 340], font_size=30, container=container)
        options_btn.attach(print_ln, "Options have not been implemented yet!")
        quit_btn = Button("Quit", location=[605, 395], font_size=30, container=container)
        quit_btn.attach(quit)
        logout_btn = Button("Log Out", location=[1200, 680], font_size=15, container=container)
        logout_btn.attach(logout)


class ConnectMenu:
    def __init__(self, container, ip="127.0.0.1", port="8007"):
        title_text = Text("Connect to Server", location=[554, 265], font_size=22, container=container)
        ip_field = InputBox(ip, location=[513, 300], font_size=22, container=container, focused=True)
        port_field = InputBox(port, location=[513, 350], font_size=22, container=container)
        connect_btn = Button("Connect", location=[597, 400], font_size=22, container=container)
        connect_btn.attach(connect, ip_field, port_field)
        back_btn = Button("Back", location=[613, 440], font_size=22, container=container)
        back_btn.attach(main_menu)


class OptionsMenu:
    def __init__(self, container, options):
        title_text = Text("Options", location=[602, 265], font_size=22, container=container)


def print_ln(value):
    print(value)


def login(username_field, password_field):
    if len(username_field.get_text()) < 4:
        print("Username is too short!")
        return
    if len(password_field.get_text()) < 4:
        print("Password is too short!")
        return
    event = pygame.event.Event(pygame.USEREVENT, name="login",
                               data={"username": username_field.get_text(), "password": password_field.get_text()})
    pygame.event.post(event)


def logout():
    event = pygame.event.Event(pygame.USEREVENT, name="logout")
    pygame.event.post(event)


def main_menu():
    event = pygame.event.Event(pygame.USEREVENT, name="main_menu")
    pygame.event.post(event)


def play():
    event = pygame.event.Event(pygame.USEREVENT, name="play")
    pygame.event.post(event)


def connect(ip_field, port_field):
    try:
        int(port_field.get_text())
    except:
        port_field.set_text("8007")
    event = pygame.event.Event(pygame.USEREVENT, name="connect",
                               data={"ip": ip_field.get_text(), "port": port_field.get_text()})
    pygame.event.post(event)
    data_file = open("..\\data\\" + get_b64_name("connection") + ".dat", 'w')
    data_file.write(base64.b64encode(json.dumps([ip_field.get_text(), port_field.get_text()], data_file).encode()).decode())
    data_file.close()


def quit():
    event = pygame.event.Event(pygame.USEREVENT, name="quit")
    pygame.event.post(event)
