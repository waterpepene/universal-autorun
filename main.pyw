from functions import *

control = ThreadControl()
control.start()

while "Running":
    window_list = enum_process_windows()
    game_running = False
    active_window = GetWindowText(GetForegroundWindow())

    for game in read_games():
        if search(game, active_window):
            game_running = True
            break

    if game_running:
        control.resume()
    else:
        control.pause()

    sleep(1)



