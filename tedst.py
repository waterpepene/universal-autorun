from win32api import GetAsyncKeyState
from win32con import VK_ADD, VK_CONTROL

if GetAsyncKeyState(VK_CONTROL):
    print("a")