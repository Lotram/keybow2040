import board
import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from src.control import HIDAction, IRAction, IRLayer, KeyboardLayer
from src.ir_remotes.remote import BenQ, Feintech, Lumene, Tangent


# Set up the keyboard and layout
keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)

# Set up consumer control (used to send media key presses)
consumer_control = ConsumerControl(usb_hid.devices)

ir_pin = board.INT

benq = BenQ(ir_pin)
lumene = Lumene(ir_pin)
sonos = Tangent(ir_pin)
feintech = Feintech(ir_pin)


layers = [
    KeyboardLayer(
        name="Kodi",
        key_map={
            (2, 3): HIDAction(
                consumer_control, ConsumerControlCode.VOLUME_DECREMENT, chr(57860)
            ),
            (1, 0): HIDAction(
                consumer_control, ConsumerControlCode.SCAN_PREVIOUS_TRACK, chr(57867)
            ),
            (1, 3): HIDAction(consumer_control, ConsumerControlCode.MUTE, chr(57858)),
            (2, 0): HIDAction(
                consumer_control, ConsumerControlCode.PLAY_PAUSE, chr(57868)
            ),
            (3, 3): HIDAction(
                consumer_control, ConsumerControlCode.VOLUME_INCREMENT, chr(57859)
            ),
            (3, 0): HIDAction(
                consumer_control, ConsumerControlCode.SCAN_NEXT_TRACK, chr(57866)
            ),
            (1, 1): HIDAction(keyboard, Keycode.LEFT_ARROW, chr(57646)),
            (2, 1): HIDAction(keyboard, Keycode.DOWN_ARROW, chr(57644)),
            (3, 1): HIDAction(keyboard, Keycode.RIGHT_ARROW, chr(57645)),
            (2, 2): HIDAction(keyboard, Keycode.UP_ARROW, chr(57643)),
            (1, 2): HIDAction(keyboard, Keycode.ENTER, "\u23CE"),
            (3, 2): HIDAction(keyboard, Keycode.BACKSPACE, "\u232B"),
            (0, 3): HIDAction(keyboard, Keycode.ESCAPE, "Esc"),
        },
        rgb=(255, 0, 255),
        keyboard=keyboard,
        consumer_control=consumer_control,
    ),
    IRLayer(
        name="Sonos",
        key_map={
            # configured to mute Sonos
            (1, 3): IRAction(sonos, Tangent.Code.KEY_ENTER, chr(57858)),
            (2, 3): IRAction(sonos, Tangent.Code.VOLUME_DECREMENT, chr(57860)),
            (3, 3): IRAction(sonos, Tangent.Code.VOLUME_INCREMENT, chr(57859)),
        },
        rgb=(0, 255, 255),
    ),
    IRLayer(
        name="Videoproj",
        key_map={
            (1, 3): IRAction(benq, BenQ.Code.MUTE, chr(57858)),
            (2, 3): IRAction(benq, BenQ.Code.VOLUME_DECREMENT, chr(57860)),
            (3, 3): IRAction(benq, BenQ.Code.VOLUME_INCREMENT, chr(57859)),
            (1, 2): IRAction(benq, BenQ.Code.KEY_POWER_ON, "ON"),
            (3, 2): IRAction(benq, BenQ.Code.KEY_POWER_OFF, "OFF"),
            (0, 1): IRAction(lumene, Lumene.Code.DOWN, chr(57441)),
            (0, 3): IRAction(lumene, Lumene.Code.STOP, chr(57433)),
            (0, 2): IRAction(lumene, Lumene.Code.UP, chr(57440)),
        },
        rgb=(255, 255, 0),
    ),
    IRLayer(
        name="Feintech",
        key_map={
            (1, 0): IRAction(feintech, Feintech.Code.ONE, chr(57706)),
            (2, 0): IRAction(feintech, Feintech.Code.TWO, chr(57707)),
            (3, 0): IRAction(feintech, Feintech.Code.THREE, chr(57708)),
            (2, 1): IRAction(feintech, Feintech.Code.FOUR, chr(57709)),
            (1, 1): IRAction(feintech, Feintech.Code.DOWN, chr(57441)),
            (3, 1): IRAction(feintech, Feintech.Code.UP, chr(57440)),
            (1, 2): IRAction(feintech, Feintech.Code.ON, "ON"),
            (3, 2): IRAction(feintech, Feintech.Code.OFF, "OFF"),
        },
        rgb=(255, 90, 70),
    ),
]
