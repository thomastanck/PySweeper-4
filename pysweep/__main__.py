#!/usr/bin/python3

def pushwindowtotop():
    import os, platform, sys

    if platform.system() == 'Darwin':  # How Mac OS X is identified by Python
        try:
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
        except:
            pass
        try:
            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "{}" to true' '''.format(os.path.basename(sys.executable)))
        except:
            pass

def main():
    # from .pysweep import mw

    import tkinter

    tk = tkinter.Tk()
    tk.title('PySweeper')
    tk.grab_set()
    # mw.init(tk)

    # from .gamemodemanager import GameModeManager # To initialise the game mode manager (it needs to know the menu has been initialised)
    # GameModeManager.init_game_mode_manager()

    pushwindowtotop()
    tk.mainloop()
    try:
        tk.destroy()
    except tkinter.TclError as e:
        pass

# if __name__ == '__main__':
main()
