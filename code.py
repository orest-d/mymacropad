from app import *
from adafruit_hid.keycode import Keycode

AppContainer(
    Screen("Hello",[
      Key(0, "Hello").color(10,10,10,50).color(0,0,0,50),
      Key(1, ", ", (0,10,0)),
      Key(2, "world", (0,0,10)),
      Key(3, [Keycode.WINDOWS, Pause(0.4), "netflix", Pause(0.4), Keycode.RETURN, Goto("Netflix")], (20,1,0)),
    ]),
    Screen("Screen 2",[
      Key(0, "Test").color(10,10,10,50).color(0,0,0,100),
      Key(1, "***").color(0,0,0,50).color(10,10,10,50).color(0,0,0,50),
      Key(2, "TEST").color(0,0,0,100).color(10,10,10,50),
      Key(3, (Keycode.WINDOWS, Keycode.E), (10,9,0)),
      Key(4, [Keycode.WINDOWS, Pause(0.4), "notepad", Pause(0.4), Keycode.RETURN, Goto("Notepad")], (10,9,8))
    ]),
    Screen("Notepad",[
      Key(0, (Keycode.CONTROL, Keycode.O)).color(0,10,0,1),
    ]),
    Screen("Netflix",[
      Key(0, PLAY_PAUSE).color(0,10,0,1),
    ]),
    Colors()
).run()
