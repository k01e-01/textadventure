import rich
import time
import datetime
        
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.style import Style
from rich.color import Color
from rich.color_triplet import ColorTriplet
from rich.layout import Layout
from pynput import keyboard, mouse


class AnyKeyContinue:

    def __init__(self, console: Console):
        self.text = "Hi! It is recomended that you decrease the console font size significantly for a better playing experience. Have fun!\n\nPress any key to continue..."
        self.console = console
        self.dim = False
        self.brightness = 255
        

    def update(self):

        height = self.console.height
        width = self.console.width
        
        br = self.brightness
        style = Style(color=Color.from_triplet(ColorTriplet(br,br,br)))

        if self.dim:
            self.brightness -= 28
        
        if self.brightness < 0:
            style = Style(color="black")
        
        if self.brightness < -256:
            return None

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

            style="color(15) on black"
        )

        return renderable
    
    def keyPress(self, key, pressed):

        self.dim = True


class Menu:

    def __init__(self, console: Console):
        self.console = console
    
    def update(self):

        renderable = Layout()

        renderable.split_row(
            Layout(name="left", ratio=6),
            Layout(name="saveselect", ratio=3)
        )
        renderable["left"].split_column(
            Layout(name="controls"),
            Layout(name="settings")
        )

        return renderable



class LiveApp:

    def __init__(self, console: Console):
        self.console = console
        self.framecount = -1
        self.state = 0


        self.screens = [
            AnyKeyContinue(console=console),
            Menu(console=console)
        ]


    def update(self):
        if self.state == -1: return None

        self.framecount += 1

        renderable = self.screens[self.state].update()

        if renderable == None:
            self.state += 1
            renderable = self.screens[self.state].update()

        return renderable
    

    def on_press(self, key):
        if key == keyboard.Key.esc:
            self.state = -1
        
        try: self.screens[self.state].keyPress(key, True)
        except: pass

    def on_release(self, key):
        try: self.screens[self.state].keyPress(key, False)
        except: pass
    
    def on_move(self, x, y):
        try: self.screens[self.state].mouseMove(x, y)
        except: pass
    
    def on_click(self, x, y, button, pressed):
        try: self.screens[self.state].mousePress(x, y, button, pressed)
        except: pass
    
    def on_scroll(self, x, y, dx, dy):
        try: self.screens[self.state].mousePress(x, y, dx, dy)
        except: pass
    





    


def main():

    console = Console()
    liveapp = LiveApp(console=console)

    keyListener = keyboard.Listener(
        on_press=liveapp.on_press,
        on_release=liveapp.on_release,
        suppress=True
    )
    keyListener.start()

    mosListener = mouse.Listener(
        on_move=liveapp.on_move,
        on_click=liveapp.on_click,
        on_scroll=liveapp.on_scroll,
        suppress=True
    )
    mosListener.start()

    with Live(renderable = None, console = console, refresh_per_second = 20, transient=True) as live:

        try:
            while True:
                starttime = time.time()

                renderable = liveapp.update()
                live.update(renderable)

                if renderable == None: break

                timedelta = time.time() - starttime

                if timedelta < 0.05:
                    time.sleep(0.05 - timedelta)
                

        except KeyboardInterrupt:
            pass
            
        keyListener.stop()
        mosListener.stop()



if __name__ == "__main__":
    main()