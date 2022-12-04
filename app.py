import board
import digitalio
import time
import neopixel
import json
from adafruit_macropad import MacroPad
from adafruit_hid.consumer_control_code import ConsumerControlCode

print("Hello App")
MAXTICKS = 0xFFFFFFF
class AppContainer:
    def __init__(self, *apps):
        self.apps=apps
        self.active_index = 0
        self.refresh=True
        self.ticks=0

    def goto(self, app):
        self.refresh=True
        if type(app) == int:
            self.active_index=(app+len(self.apps))%len(self.apps)
        else:
            for i,a in enumerate(self.apps):
                if a == app or a.name == app:
                    self.active_index = i
                    break

    def active_app(self):
        return self.apps[self.active_index]

    def next_app(self):
        self.goto(self.active_index+1)

    def previous_app(self):
        self.goto(self.active_index-1)

    def do_tick(self, container):
        #print("do tick from container", self.active_app().name)
        self.active_app().do_tick(container)

    def run(self):
        self.macropad=MacroPad()
        last_encoder = self.macropad.encoder
        self.delta_encoder = 0

        while True:
            self.key_event = self.macropad.keys.events.get()
            new_encoder = self.macropad.encoder
            self.delta_encoder = new_encoder-last_encoder
            last_encoder = new_encoder
            aa = self.active_app()
            if not aa.capture_encoder and self.delta_encoder:
                if self.delta_encoder>0:
                    self.next_app()
                else:
                    self.previous_app()
                continue
            if self.refresh:
                self.text = self.macropad.display_text(title=aa.name)
                aa.init(self)
                self.refresh=False
            self.do_tick(self)
            self.text.show()
            self.ticks+=1
            if self.ticks>MAXTICKS:
                self.ticks=0


class App:
    capture_encoder=False
    def __init__(self, name):
        self.name = name
    def init(self, container):
        pass
    def do_tick(self, container):
        pass
class Key:
    def __init__(self, n, action=None, *frames):
        self.frames=list(frames)
        self.n = n
        self.action=action

    def color(self, r, g, b, length=1):
        for i in range(length):
            self.frames.append((r,g,b))
        return self

    def do(self, app, container, x):
        if x is None:
            return
        if type(x) == str:
            container.macropad.keyboard_layout.write(x)
        elif type(x) == int:
            container.macropad.keyboard.send(x),
        elif type(x) == tuple:
            container.macropad.keyboard.send(*x),
        elif type(x) == list:
            for xx in x:
                self.do(app, container, xx)
        else:
            x(app, container)

    def do_action(self, app, container):
        self.do(app, container, self.action)
#        if self.action is not None:
#            if type(self.action) == str:
#                container.macropad.keyboard_layout.write(self.action)
#            else:
#                self.action(self, app, container)

    def tick_color(self, ticks):
        if len(self.frames):
            t=ticks%len(self.frames)
            return self.frames[t]
        else:
            return (0,0,0)

class Pause:
    def __init__(self, t):
        self.t=t
    def __call__(self, *arg):
        time.sleep(self.t)

class Goto:
    def __init__(self, to):
        self.to=to
    def __call__(self, app, container):
        container.goto(self.to)

class CC:
    def __init__(self, cc):
        self.cc=cc
    def __call__(self, app, container):
        container.macropad.consumer_control.send(self.cc)

BRIGHTNESS_DECREMENT = CC(ConsumerControlCode.BRIGHTNESS_DECREMENT)
BRIGHTNESS_INCREMENT = CC(ConsumerControlCode.BRIGHTNESS_INCREMENT)
EJECT = CC(ConsumerControlCode.EJECT)
FAST_FORWARD = CC(ConsumerControlCode.FAST_FORWARD)
MUTE = CC(ConsumerControlCode.MUTE)
PLAY_PAUSE = CC(ConsumerControlCode.PLAY_PAUSE)
RECORD = CC(ConsumerControlCode.RECORD)
REWIND = CC(ConsumerControlCode.REWIND)
SCAN_NEXT_TRACK = CC(ConsumerControlCode.SCAN_NEXT_TRACK)
SCAN_PREVIOUS_TRACK = CC(ConsumerControlCode.SCAN_PREVIOUS_TRACK)
STOP = CC(ConsumerControlCode.STOP)
VOLUME_DECREMENT = CC(ConsumerControlCode.VOLUME_DECREMENT)
VOLUME_INCREMENT = CC(ConsumerControlCode.VOLUME_INCREMENT)

class Move:
    def __init__(self, x, y):
        self.x=x
        self.y=y
    def __call__(self, app, container):
        container.macropad.mouse.move(self.x, self.y)

class Screen(App):
    def __init__(self, name, keys):
        self.name = name
        self.keys = keys
    def init(self, container):
        pixels = container.macropad.pixels
        for i in range(12):
            pixels[i]=(0,0,0)
        for key in self.keys:
            pixels[key.n]=key.tick_color(0)

    def do_tick(self, container):
        t = container.ticks
        pixels = container.macropad.pixels
        key_event = container.key_event
        for key in self.keys:
            pixels[key.n]=key.tick_color(t)
        if key_event and key_event.pressed:
            for key in self.keys:
                if key_event.key_number == key.n:
                    key.do_action(self, container)

class Colors(App):
    capture_encoder=True
    ESC_KEY = 0
    RED_KEY = 3
    GREEN_KEY = 4
    BLUE_KEY = 5
    DEMO = 6,7,8,9,10,11

    RED_MODE = "Red"
    GREEN_MODE = "Green"
    BLUE_MODE = "Blue"

    def __init__(self, name="Colors"):
        App.__init__(self, name)

    def init(self, container):
        macropad = container.macropad
        macropad.pixels[self.ESC_KEY]=(10,0,0)
        macropad.pixels[self.RED_KEY]=(5,0,0)
        macropad.pixels[self.GREEN_KEY]=(0,5,0)
        macropad.pixels[self.BLUE_KEY]=(0,0,5)

        self.color = [0,0,0]
        self.offset_value = 0
        self.index=0
        self.mode=self.RED_MODE
        self.last_value=0

    def _do_tick(self, container):
        print("TICK",container.ticks)
        macropad = container.macropad
        if int(container.ticks/20)%2:
            macropad.pixels[self.ESC_KEY]=(0,10,0)
        else:
            macropad.pixels[self.ESC_KEY]=(0,0,10)

    def do_tick(self, container):
        key_event = container.key_event
        macropad = container.macropad
        text=container.text
#        text[1].text="Tick "+str(container.ticks)
        t = int(container.ticks)%20
        if t>10:
            t=20-t
        macropad.pixels[self.ESC_KEY]=(t,0,0)

        if key_event:
            if key_event.pressed and key_event.key_number in (self.RED_KEY, self.GREEN_KEY, self.BLUE_KEY):
                self.mode = {self.RED_KEY:self.RED_MODE, self.BLUE_KEY:self.BLUE_MODE, self.GREEN_KEY:self.GREEN_MODE}.get(key_event.key_number)
                self.index = {self.RED_KEY:0, self.GREEN_KEY:1, self.BLUE_KEY:2}.get(key_event.key_number)
            if key_event.pressed and key_event.key_number == self.ESC_KEY:
                container.goto(0)
        if self.mode == self.RED_MODE:
            macropad.pixels[self.RED_KEY]=(255,0,0)
            macropad.pixels[self.GREEN_KEY]=(0,5,0)
            macropad.pixels[self.BLUE_KEY]=(0,0,5)
        if self.mode == self.GREEN_MODE:
            macropad.pixels[self.RED_KEY]=(5,0,0)
            macropad.pixels[self.GREEN_KEY]=(0,255,0)
            macropad.pixels[self.BLUE_KEY]=(0,0,5)
        if self.mode == self.BLUE_MODE:
            macropad.pixels[self.RED_KEY]=(5,0,0)
            macropad.pixels[self.GREEN_KEY]=(0,5,0)
            macropad.pixels[self.BLUE_KEY]=(0,0,255)

        self.color[self.index] += container.delta_encoder
        self.color[self.index] = max(min(self.color[self.index],255),0)

        for i in self.DEMO:
            macropad.pixels[i]=self.color

        text[0].text=self.mode
        text[1].text=str(self.color)


