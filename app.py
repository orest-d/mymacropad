import board
import digitalio
import time
import neopixel
import json
from adafruit_macropad import MacroPad
from adafruit_hid.consumer_control_code import ConsumerControlCode

print("Hello App")

class AnimationMixin:
    def loop(self):
        return Loop(self)
    def then(self, a, after_steps=None):
        return Then(self, a, after_steps)
    def interpolate(self, color1, color2, steps):
        return Then(self, Interpolate(color1, color2, steps))
    def interpolate_to(self, color, steps):
        return Then(self, Interpolate(self.last(), color, steps))
    def color(self, r, g, b, steps=1):
        return Then(self, Interpolate((r,g,b), (r,g,b), steps))
    def black(self, steps=1):
        return self.color(0,0,0)
    def bounce(self):
        return Bounce(self)
    def offset(self, n):
        return Offset(self, n)
    def pad(self, color=(0,0,0)):
        return Then(self, Interpolate(color, color, 1).loop())
    def pad_last(self):
        last = self.last()
        if last is None:
            return self.then_error()
        return self.pad(self.last())
    def then_error(self):
        return self.then(Animation().color(255,0,0,10).color(255,255,0,5).black(10).loop())
    def __add__(self, other):
        return Add(self, other)
    def last(self):
        if self.is_finite():
            last = None
            for x in self:
                last=x
            return last
        else:
            return next(iter(self))

class Animation(AnimationMixin):
    def __init__(self, *a):
        self.a=list(a)
    def add(self,x):
        self.a.append(x)
        return self
    def is_finite(self):
        return all(x.is_finite() for x in self.a)
    def __len__(self):
        if len(self.a):
            return sum(len(x) for x in self.a) if self.is_finite() else None
        else:
            return 0

    def __iter__(self):
        for x in self.a:
            if type(x)==tuple:
                yield x
            for y in x:
                yield y
    def clone(self):
        return Animation(*[x.clone() for x in self.a])

class Add(AnimationMixin):
    def __init__(self, a, b):
       self.a=a
       self.b=b
    def is_finite(self):
        return self.a.is_finite() and self.b.is_finite()

    def __len__(self):
        if not self.is_finite():
            return None
        return max(len(self.a),len(self.b))

    def __iter__(self):
        length = len(self)
        if length is None:
            while True:
                for c1, c2 in zip(self.a.pad(), self.b.pad()):
                    yield (min(c1[0]+c2[0],255), min(c1[1]+c2[1],255), min(c1[2]+c2[2],255))
        else:
            for i in range(length):
                yield (min(c1[0]+c2[0],255), min(c1[1]+c2[1],255), min(c1[2]+c2[2],255))
    def clone(self):
        return Add(self.a.clone(), self.b.clone())


class Offset(AnimationMixin):
    def __init__(self, a, n=None):
       self.a=a
       self.n=n
    def is_finite(self):
        return self.a.is_finite()
    def __len__(self):
        return None if len(self.a) is None else len(self.a)-self.n
    def __iter__(self):
        x = iter(self.a)
        for i in range(self.n):
            next(x)
        for y in x:
            yield y
    def clone(self):
        return Offset(self.a.clone(), self.n)

class Loop(AnimationMixin):
    def __init__(self, a, n=None):
       self.a=a
       self.n=n
    def is_finite(self):
        return False if self.n is None else self.a.is_finite()
    def __len__(self):
        return None if self.n is None or len(self.a) is None else self.n*len(self.a)
    def __iter__(self):
        if self.n is None:
            while True:
                for x in self.a:
                    yield x
        else:
            for i in range(self.n):
                for x in self.a:
                    yield x
    def clone(self):
        return Loop(self.a.clone(), self.n)

class Bounce(AnimationMixin):
    def __init__(self, a, n=None):
       self.a=a
       self.n=n
    def is_finite(self):
        return False if self.n is None else self.a.is_finite()
    def __len__(self):
        return None if self.n is None or len(self.a) is None else 2*self.n*len(self.a)
    def __iter__(self):
        n = 1 if self.n is None else self.n
        while True:
            for i in range(n):
                buffer=[]
                for x in self.a:
                    buffer.append(x)
                    yield x
                for x in reversed(buffer):
                    yield x
            if self.n is not None:
                break
    def clone(self):
        return Bounce(self.a.clone(), self.n)

class Then(AnimationMixin):
    def __init__(self, first, then, steps=None):
       self._first=first
       self._then=then
       self._steps=steps
    def is_finite(self):
        if self._steps is None:
            return self._first.is_finite() and self._then.is_finite()
        else:
            return self._then.is_finite()

    def __len__(self):
        if self._steps is None:
            if len(self._first) is None or len(self._then) is None:
                return None
            return len(self._first) + len(self._then)
        else:
            if len(self._then) is None:
                return None
            return self._steps + len(self._then)

    def __iter__(self):
        if self._steps is None:
            for x in self._first:
                yield x
        else:
            for i,x in zip(range(self._steps),self._first):
                yield x
        for x in self._then:
            yield x
    def clone(self):
        return Then(self._first.clone(), self._then.clone(), self._steps)

class Interpolate(AnimationMixin):
    def __init__(self, color1, color2, steps):
        self.color1=color1
        self.color2=color2
        self.steps=steps
    def __len__(self):
        return self.steps
    def is_finite(self):
        return False
    def __iter__(self):
        if self.steps<=1:
            yield self.color1
        else:
            r1,g1,b1=self.color1
            r2,g2,b2=self.color2
            for i in range(self.steps):
                w = i/(self.steps-1.0)
                r = int((1-w)*r1 + w*r2)
                g = int((1-w)*g1 + w*g2)
                b = int((1-w)*b1 + w*b2)
                yield (r,g,b)
    def clone(self):
        return Interpolate(self.color1, self.color2, self.steps)



MAXTICKS = 0xFFFFFFF
class AppContainer:
    def __init__(self, *apps):
        self.stack=[]
        self.apps=apps
        self.active_index = 0
        self.refresh=True
        self.ticks=0

    def push(self, apps, active_index=0):
        self.stack.append((self.apps,self.active_index))
        self.apps=apps
        self.active_index=active_index
        self.refresh=True
        self.ticks=0
        return self

    def pop(self):
        if len(self.stack):
            self.apps, self.active_index = self.stack.pop()
            self.refresh=True
            self.ticks=0
        return self

    def goto(self, app):
        self.refresh=True
        self.ticks=0
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
    def __init__(self, n, action=None, *animation):
        self.color_animation=Animation(*animation)
        self.n = n
        self.action=action
        self.first_tick=None
        self.color_iterator=None

    def init(self, tick=0):
        self.first_tick = tick
        self.color_iterator = iter(self.color_animation.pad_last())

    def loop(self):
        self.color_animation=self.color_animation.loop()
        return self

    def color(self, r, g, b, length=1):
        if length == 1:
            self.color_animation.add((r,g,b))
        else:
            self.color_animation.add(Interpolate((r,g,b),(r,g,b),length))

        return self

    def with_animation(self, a):
        self.color_animation=a
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
        return next(self.color_iterator)

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

class Push:
    def __init__(self, *apps):
        self.apps = list(apps)
    def __call__(self, app, container):
        container.push(self.apps)

class Pop:
    def __call__(self, app, container):
        container.pop()

POP = Pop()

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
        self.first_tick=None
    def init(self, container):
        self.first_tick = container.ticks
        pixels = container.macropad.pixels
        for i in range(12):
            pixels[i]=(0,0,0)
        for key in self.keys:
            key.init()
            pixels[key.n]=key.tick_color(0)

    def key(self, i):
        for key in self.keys:
            if key.n==i:
                return key

    def do_tick(self, container):
        t = container.ticks - self.first_tick
        pixels = container.macropad.pixels
        key_event = container.key_event
        for key in self.keys:
            pixels[key.n]=key.tick_color(t)
        if key_event and key_event.pressed:
            for key in self.keys:
                if key_event.key_number == key.n:
                    key.do_action(self, container)

#    def animate_function(self, keys, period, init, color1, color2, f):
#        from math import sin, pi
#        if keys is None:
#            keys = [k.n for k in self.keys]
#        keys = list(keys)
#        if init:
#            colors1 = [(self.key(k).init_frames[:1]+[color1])[0] for k in keys]
#            colors2 = [(self.key(k).init_frames[1:2]+[color2])[0] for k in keys]
#            for k in keys:
#                self.key(k).init_frames=[]
#        else:
#            colors1 = [(self.key(k).frames[:1]+[color1])[0] for k in keys]
#            colors2 = [(self.key(k).frames[1:2]+[color2])[0] for k in keys]
#            for k in keys:
#                self.key(k).frames=[]
#        for t in range(period):
#            for i,k in enumerate(keys):
#                intensity = f(i,t,period)
#                color = tuple(int(a*(1-intensity) + b*intensity) for a,b in zip(colors1[i], colors2[i]))
#                if init:
#                    self.key(k).init_frames.append(color)
#                else:
#                    self.key(k).frames.append(color)
#        return self
#
#    def animate_wave(self, keys, period=50, init=False, color1=(10,10,10), color2=(0,0,0)):
#        from math import sin, pi
#        def f(i, t, period):
#            intensity = sin((t+i)*pi/period)
#            return intensity * intensity
#        return self.animate_function(keys, period, init, color1, color2, f)
#
#    def animate_transition(self, keys, period=50, init=False, color1=(10,10,10), color2=(0,0,0)):
#        return self.animate_function(keys, period, init, color1, color2, lambda i, t, period: ((t + i)%period)/(period-1))

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


