from app import *
from adafruit_hid.keycode import Keycode

ESC_ANIMATION=Interpolate((10,0,0),(0,0,0),50).loop()
AppContainer(
    Screen("ROOT", [
      Key(0, Push(
        Screen("Linux Apps",[
          Key(0, [
            (Keycode.ALT, Keycode.F2), Pause(0.5), "mate-terminal", Pause(0.1), Keycode.RETURN, Pause(0.5),
            "mc", Keycode.RETURN, Pause(0.5),
            (Keycode.ALT, Keycode.V), Keycode.DOWN_ARROW, Keycode.DOWN_ARROW, Keycode.RETURN,
            Keycode.F11,
            Goto("Midnight Commander")]).with_animation(Interpolate((8,8,6),(0,0,10),50).loop()),
          Key(11, Pop()).with_animation(ESC_ANIMATION),
        ]),
        Screen("Midnight Commander",[
          Key(0, [(Keycode.ALT, Keycode.V), Keycode.DOWN_ARROW, Keycode.DOWN_ARROW, Keycode.DOWN_ARROW, Keycode.RETURN], (10,10,10)).loop(),
          Key(1, [(Keycode.ALT, Keycode.V), Keycode.DOWN_ARROW, Keycode.DOWN_ARROW, Keycode.RETURN], (10,10,10)).loop(),
          Key(2, [Keycode.ESCAPE, '0'], (10,0,0)).loop(),
          Key(3, ['cd ..\n'], (0,10,20)).loop(),
          Key(4, ['cd ~\n'], (0,0,20)).loop(),
        ])
      )).with_animation(Interpolate((0,0,0),(0,50,0),50).bounce()),
      Key(3, Push(
        Screen("Hello",[
          Key(0, "Hello").color(10,10,10,50).color(0,0,0,50).loop(),
          Key(1, ", ", (0,10,0)).loop(),
          Key(2, "world", (0,0,10)).loop(),
          Key(3, [Keycode.WINDOWS, Pause(0.4), "netflix", Pause(0.4), Keycode.RETURN, Goto("Netflix")], (20,1,0)).loop(),
          Key(6, Pop()).color(10,0,0,50).color(0,0,0,50).loop(),
        ]),
        Colors()
      )).color(10,10,0,10).color(8,8,0,10).color(6,6,0,10).color(4,4,0,10).color(2,2,0,10).color(0,0,0,50).loop()
    ])
).run()

#AppContainer(
#    Screen("ROOT", [
#      Key(0, Push(
#        Screen("Subscreen 1", [
#          Key(1, Pop(), (0,0,10))
#        ]),
#        Screen("Subscreen 2", [
#          Key(2, Pop(), (10,0,10))
#        ])
#        )
#      ).color(0,10,0,40).color(0,0,0,40)])
#).run()
