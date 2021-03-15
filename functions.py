import threading
from win32gui import GetForegroundWindow, GetWindowText, EnumWindows
from win32api import GetWindowLong, GetAsyncKeyState
from win32con import GWL_STYLE, WS_VISIBLE, VK_ADD, VK_RCONTROL, VK_NUMPAD8
from win32process import GetWindowThreadProcessId
from time import sleep
import os
import ctypes
from re import search

SendInput = ctypes.windll.user32.SendInput
W_KEY = 0x11

# Code taken from https://github.com/Sentdex/pygta5/blob/master/directkeys.py
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
def press_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


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

            if GetAsyncKeyState(VK_NUMPAD8) and GetAsyncKeyState(VK_ADD):  # checks if the + button was clicked
                press_key(W_KEY)
                press_key(VK_NUMPAD8)

            elif GetAsyncKeyState(VK_ADD):
                press_key(W_KEY)

            if GetAsyncKeyState(VK_RCONTROL):
                release_key(W_KEY)
                release_key(VK_NUMPAD8)

            sleep(0.1)

    def pause(self):
        self.__flag.clear()  # Set to False to block the thread

    def resume(self):
        self.__flag.set()  # Set to True, let the thread stop blocking

    def stop(self):
        self.__flag.set()  # Resume the thread from the suspended state, if it is already suspended
        self.__running.clear()  # Set to False


def enum_windows_proc(wnd, param):
    pid = param.get("pid", None)
    data = param.get("data", None)

    if pid is None or GetWindowThreadProcessId(wnd)[1] == pid:
        text = GetWindowText(wnd)
        if text:
            if (GetWindowLong(wnd, GWL_STYLE) & WS_VISIBLE) and data is not None:
                data.append(text)


def enum_process_windows(pid=None) -> list:
    data = []
    param = {
        "pid": pid,
        "data": data,
    }
    EnumWindows(enum_windows_proc, param)

    return data


def find_games_folder() -> str:
    current_dir = os.getcwd()
    games_file_name = "games.txt"
    games_file_path = os.path.join(current_dir, games_file_name)

    return str(games_file_path)


def read_games():
    games_path = find_games_folder()

    with open(fr"{games_path}", "r") as games_file:
        for game in games_file:
            yield game.strip("\n")
