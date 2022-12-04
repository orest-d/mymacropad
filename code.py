from app import *
from adafruit_hid.keycode import Keycode

AppContainer(
    Screen("Hello",[
      Key(0, "Hello").color(10,10,10,50).color(0,0,0,50),
      Key(1, ", ", (0,10,0)),
      Key(2, "world", (0,0,10)),
    ]),
    Screen("Screen 2",[
      Key(0, "Test").color(10,10,10,50).color(0,0,0,100),
      Key(1, "***").color(0,0,0,50).color(10,10,10,50).color(0,0,0,50),
      Key(2, "TEST").color(0,0,0,100).color(10,10,10,50),
      Key(3, (Keycode.WINDOWS, Keycode.E), (10,9,0)),
      Key(4, [Keycode.WINDOWS, Pause(0.2), "notepad", Pause(0.2), Keycode.RETURN], (10,9,8))
    ]),
    Colors()
).run()
