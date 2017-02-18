#!/usr/bin/python3

from PIL import Image, ImageTk
import tkinter

from .display import Display, DisplayImage, TileState

from .skin import Skin
from .dirstruct import Multi, Dir

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

    # Hack to look at the display
    skindir = 'images_d_tiles'
    skin = Skin(Multi(Dir(skindir), Dir('images')))
    skin.preload_skin()
    displaycanvas = DisplayCanvas(tk, skin)
    displaycanvas.pack()

    displaycanvas.display.draw()
    displaycanvas.display.tiles[4][2].state = TileState.Number[4]
    displaycanvas.display.tiles[4][2].draw()
    displaycanvas.draw()

    pushwindowtotop()
    tk.mainloop()
    try:
        tk.destroy()
    except tkinter.TclError as e:
        pass

if __name__ == '__main__':
    main()

# Hack to look at the screen. I stole this from the previous code :P
class DisplayCanvas(tkinter.Canvas):
    """ Puts the Display Part onto a Canvas """
    def __init__(self, master, skin):
        self.master = master
        self.skin = skin

        self.displayimg = DisplayImage(None)

        self.display = Display(self.displayimg, skin)

        self.size = self.display.size

        super().__init__(self.master, width=self.size[0], height=self.size[1], highlightthickness=0)

        self.img = Image.new(size=self.size, mode="RGBA")
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.displayimg.pil_image = self.img
        self.create_image(0, 0, image=self.tkimg, anchor='nw')

        self.display.draw()
        self.draw()

    def draw(self):
        self.tkimg.paste(self.img)
