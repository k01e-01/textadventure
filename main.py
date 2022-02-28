#
#                       text adventure v0.0
#
#   by K01e (harry)
#
#   why did i do this
#   all i needed to do was write some print statements and thats it
#   i better get good marks :(
#

import rich
import pynput
import time
import json
import numpy as np
import PIL
import os
import re
        
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.style import Style
from rich.color import Color
from rich.color_triplet import ColorTriplet
from rich.layout import Layout
from pynput import keyboard, mouse
from PIL import Image
from os import listdir
from os.path import isfile, join

class AnyKeyContinue:

    def __init__(self, console: Console):
        self.text = "Hi! It is recomended that you decrease the console font size significantly for a better playing experience. Have fun!\n\nPress any key to continue..."
        self.console = console
        self.dim = False
        self.brightness = 255
        

    def update(self):

        height = self.console.height
        width = self.console.width
        
        # i could shorten this but why would you
        # it would make more sense if i did, yuck
        br = self.brightness
        style = Style(color=Color.from_triplet(ColorTriplet(br,br,br)))

        if self.dim:
            self.brightness -= 28
        
        if self.brightness < 0:
            style = Style(color="black")
        
        if self.brightness < -256:
            return 1

        # align object inside align object
        # don't remember why
        # theres an easier way
        renderable = Align(
            Align(
                Text(self.text, justify="center", style=style),
                align="center",
                vertical="middle",
                width=70,
                height=4
            ),
            align="center",
            vertical="middle",
            height=height,
            width=width,

            style="bold white on black"
        )

        return renderable
    
    def keyPress(self, key, pressed):

        self.dim = True


class Room:

    def __init__(self, console: Console, framecount: int, roomnum: int = 0):
        self.console = console
        self.roomnum = roomnum
        self.frames = framecount
    
    def update(self):

        if self.roomnum == -1:
            return self.test()

        return self.render_layers()
    
    def get_data(self):

        # data consists of 
        # textures

        path = "./assets/textures"
        files = [(join(path, f), f.split('.')[0]) for f in listdir(path) if isfile(join(path, f))]
        textures = {}

        for file, filename in files:
            image = Image.open(file)
            textures[filename] = np.array(image)

        return (textures)

    def get_room_data(self):

        # room data consists of
        # a map of textures
        # a map of collision (walls)
        # a map of objects (stuff that does stuff)

        with open(f"./assets/room{str(self.roomnum)}/map.json") as roommap:
            roommap = json.loads(roommap.read())
        
        with open(f"./assets/room{str(self.roomnum)}/collide.json") as roomcollide:
            roomcollide = json.loads(roomcollide.read())

        with open(f"./assets/room{str(self.roomnum)}/objects.json") as roomobjects:
            roomobjects = json.loads(roomobjects.read())
        
        return (roommap, roomcollide, roomobjects)

    
    def render_layers(self):
        
        # TODO: create the other 500 lines of render_layers()
        # cant wait

        roomdata = self.get_room_data()
        data = self.get_data()


        try:
            if self.tilemap: pass
        except:
            self.tilemap = roomdata[0]
        
        try:
            if self.collisionmap: pass
        except:
            self.collisionmap = roomdata[1]
        
        try:
            if self.objects: pass
        except:
            self.objects = roomdata[2]
        

        text = Text("")

        # due to the tilesize being 8, this weird code block is nessacary
        # please dont ask
        for y in self.tilemap:
            for y2 in range(8):
                for x in y:
                    for x2 in range(8):

                        texture = data[x]
                        rgb = texture[x2][y2]

                        color = Color.from_triplet( ColorTriplet(rgb[0], rgb[1], rgb[2]) )
                        style = Style(bgcolor=color)
                        text += Text('  ', style=style)
               
                text += '\n'
        
        width = self.console.width
        height = self.console.height

        renderable = Align(
            renderable=text,
            align="center",
            vertical="middle",
            width=width,
            height=height
        )

        return renderable
        

    def test(self):

        width = self.console.width
        height = self.console.height
        
        text = Text("", justify="middle")

        testgridsize = 12*8

        # this was a mistake
        # i should lose at least one extra credit mark for this mess
        reverse = False
        for i in range(round(testgridsize)):
            reverse = not reverse
            for ii in range(round(testgridsize/2)):
                if not reverse:
                    text += Text("  ", style="red on red")
                    text += Text("  ", style="green on green")
                else:
                    text += Text("  ", style="green on green")
                    text += Text("  ", style="red on red")
            text += '\n'

        renderable = Align(
            renderable=text,
            align="center",
            vertical="middle",
            width=width,
            height=height
        )

        return renderable




class LiveApp:

    def __init__(self, console: Console):
        self.console = console
        self.framecount = -1
        self.state = 0


        self.screens = [
            AnyKeyContinue(console=console),
            Room(console=console, framecount=self.framecount, roomnum=0)
        ]


    def update(self):
        if self.state == -1: return None

        self.framecount += 1
    
        # update current screen
        # list not typed properly so vsc cant tell its a function
        # still better than replit
        renderable = self.screens[self.state].update()

        if type(renderable) == int:
            self.state += renderable
            renderable = self.screens[self.state].update()
        
        # yeah actually i did need to remove the try except block
        return renderable
    

    def on_press(self, key):
        # esc to exit at any time
        # added because i broke my computer and had to restart it
        # not kidding
        if key == keyboard.Key.esc:
            self.state = -1
        
        try: self.screens[self.state].keyPress(key, True)
        except: pass

    def on_release(self, key):
        try: self.screens[self.state].keyPress(key, False)
        except: pass




def main():

    console = Console()
    liveapp = LiveApp(console=console)

    suppress = True
    
    # key listener to catch and supress key inputs
    # hopefully it won't break my computer again
    keyListener = keyboard.Listener(
        on_press=liveapp.on_press,
        on_release=liveapp.on_release,
        suppress=suppress
    )
    keyListener.start()

    # mouse listener to supress mouse inputs 
    # mainly scrolling
    # screw scrolling >:(
    mosListener = mouse.Listener(
        suppress=suppress
    )
    mosListener.start()

    # start live loop, finally
    with Live(renderable = None, console = console, refresh_per_second = 20, transient=True) as live:

        try:
            while True:
                starttime = time.time()

                renderable = liveapp.update()
                live.update(renderable)

                if renderable == None: break

                # framerate cap 
                # gotta get that 60 fps text adventure gaming B)
                timedelta = time.time() - starttime

                if timedelta < 0.05:
                    time.sleep(0.05 - timedelta)
                
        # not actually possible anymore due to supression
        # not actually possible to remove due to laziness
        except KeyboardInterrupt:
            pass
            
        keyListener.stop()
        mosListener.stop()


# run code, fingers crossed
if __name__ == "__main__":
    main()