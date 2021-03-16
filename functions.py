import threading
from win32gui import GetForegroundWindow, GetWindowText
from win32api import GetAsyncKeyState, GetKeyState
from win32con import VK_ADD, VK_RCONTROL, VK_NUMPAD8, VK_RSHIFT
from time import sleep
import os
import ctypes
from re import search

# Code taken from https://github.com/Sentdex/pygta5/blob/master/directkeys.py
SendInput = ctypes.windll.user32.SendInput
# These keys are DirectInput scan codes and they are used because win32 keys don't work in DirectX apps
W_KEY = 0x11
NP_8 = 0x48
SHIFT_KEY = 0x2A
# C struct redefinitions
PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


# Actual Functions
# This function holds down a given key.
def press_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


# This function releases a given key.
def release_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


class ThreadControl(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(ThreadControl, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()  # The flag used to pause the thread
        self.__flag.set()  # Set to True
        self.__running = threading.Event()  # Used to stop the thread identification
        self.__running.set()  # Set running to True

    def run(self):
        while self.__running.isSet():
            self.__flag.wait()

            # checks if the '+' button and 'numpad 8' were pressed
            if GetAsyncKeyState(VK_NUMPAD8) and GetAsyncKeyState(VK_ADD):
                while GetKeyState(VK_NUMPAD8): pass  # wait until Numpad 8 is released
                press_key(NP_8)
                press_key(W_KEY)

            # checks if the 'right shift' button and '+' were pressed
            elif GetAsyncKeyState(VK_RSHIFT) and GetAsyncKeyState(VK_ADD):
                while GetKeyState(VK_RSHIFT): pass  # wait until Right Shift is released
                press_key(W_KEY)
                press_key(SHIFT_KEY)

            # checks if the '+' button was pressed
            elif GetAsyncKeyState(VK_ADD):
                press_key(W_KEY)

            # checks if the 'right ctrl' button is pressed and releases 'shift', 'w' and 'numpad 8'
            if GetAsyncKeyState(VK_RCONTROL):
                release_key(SHIFT_KEY)
                release_key(W_KEY)
                release_key(NP_8)

            sleep(0.2)

    def pause(self):
        self.__flag.clear()  # Set to False to block the thread

    def resume(self):
        self.__flag.set()  # Set to True, let the thread stop blocking

    def stop(self):
        self.__flag.set()  # Resume the thread from the suspended state, if it is already suspended
        self.__running.clear()  # Set to False


# Looks for the games.txt file in the current folder and returns the path.
def find_games_folder() -> str:
    current_dir = os.getcwd()
    games_file_name = "games.txt"
    games_file_path = os.path.join(current_dir, games_file_name)

    return str(games_file_path)


# Function used to read games from the games.txt file and yield them
def read_games():
    games_path = find_games_folder()

    with open(fr"{games_path}", "r") as games_file:
        for game in games_file:
            yield game.strip("\n")
