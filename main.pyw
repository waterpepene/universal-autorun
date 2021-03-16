from functions import *

control = ThreadControl()
control.start()

while "Running":
    game_running = False
    active_window = GetWindowText(GetForegroundWindow())    # gets the active window

    for game in read_games():
        if search(game, active_window):
            game_running = True
            break

    # starts listening for keys if the active window is in games.txt
    if game_running:
        control.resume()
    else:
        control.pause()

    sleep(1)



