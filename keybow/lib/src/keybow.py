import time
from collections import namedtuple

import board
from adafruit_is31fl3731.keybow2040 import Keybow2040 as Pixels
from digitalio import DigitalInOut, Pull
from src.utils import Matrix, number_to_xy


EVENTS = ["pressed", "held", "released", "hold_released", "tapped"]

KeyState = namedtuple("KeyState", EVENTS)
ROW_SIZE = 4


class EventHandler:
    def __init__(self, event: str, key, funcs=None):
        self.event = event
        self.key = key
        self.funcs = funcs or []

        self.state = False
        self.previous_state = False

    def update_state(self, new_state):
        self.previous_state = self.state
        self.state = new_state

        if self.state and not self.previous_state and self.funcs:
            for func in self.funcs:
                func(self.key)


_PINS = Matrix(
    board.SW0,
    board.SW1,
    board.SW2,
    board.SW3,
    board.SW4,
    board.SW5,
    board.SW6,
    board.SW7,
    board.SW8,
    board.SW9,
    board.SW10,
    board.SW11,
    board.SW12,
    board.SW13,
    board.SW14,
    board.SW15,
)


class LED:
    def __init__(self, idx, keybow, rgb=None):
        self.idx = idx
        self.keybow = keybow
        self._lit = False
        self.rgb = rgb or [0, 0, 0]

    @property
    def has_rgb(self) -> bool:
        return self.rgb != (0, 0, 0)

    def set_led_color(self, r: int, g: int, b: int):
        if (r, g, b) == (0, 0, 0):
            raise ValueError("color cannot be set to (0,0,0)")
        self.rgb = (r, g, b)

    @property
    def lit(self) -> bool:
        return self._lit

    @lit.setter
    def lit(self, state):
        if isinstance(state, tuple):
            self.set_led_color(*state)
            state = True

        elif state and not self.has_rgb:
            raise ValueError("rgb color must be defined before setting the led")

        self._lit = state
        r, g, b = self.rgb if state else (0, 0, 0)
        self.keybow._pixels.set_pixel(self.idx, r, g, b)


class Key(LED):
    """
    Represents a key on Keybow 2040, with associated switch and
    LED behaviours.

    :param idx: the key idx (0-15) to associate with the key
    """

    def __init__(
        self,
        idx: int,
        pin,
        keybow,
        hold_threshold=0.1,
        event_handlers=None,
        rgb=None,
    ):
        self.idx = idx
        self.switch = DigitalInOut(pin)
        self.switch.pull = Pull.UP
        self._pin = pin

        self.hold_threshold = hold_threshold

        self.event_handlers = {event: EventHandler(event, self) for event in EVENTS}
        if event_handlers:
            self.event_handlers.update(event_handlers)

        self._time_of_last_press = time.monotonic()
        self._time_held_for = 0

        super().__init__(idx=idx, keybow=keybow, rgb=rgb)

    def is_pressed(self) -> bool:
        """
        Returns the state of the key (0=not pressed, 1=pressed).
        """
        return not self.switch.value

    def update_elapsed_times(self, previous_pressed):
        update_time = time.monotonic()
        if not self.pressed:
            self._time_held_for = 0

        # If the key has just been pressed, then record the
        # `time_of_last_press`.
        elif not previous_pressed:
            self._time_of_last_press = update_time

        # If the key is pressed and held, then update the
        # `_time_held_for` variable.
        else:
            self._time_held_for = update_time - self._time_of_last_press

    @property
    def previous_state(self):
        return KeyState(
            *(self.event_handlers[event].previous_state for event in EVENTS)
        )

    @property
    def newly_pressed(self):
        pressed_handler = self.event_handlers["pressed"]
        return pressed_handler.state and not pressed_handler.previous_state

    def update(self):
        # Updates the state of the key and updates all of its
        # attributes.

        # Keys get locked during the debounce time.

        _previous_state = self.previous_state

        self.pressed = self.is_pressed()

        self.held = self.pressed and self._time_held_for > self.hold_threshold

        self.released = not self.pressed and _previous_state.pressed
        self.tapped = self.released and not _previous_state.held
        self.hold_released = self.released and _previous_state.held

        self.update_elapsed_times(_previous_state.pressed)

        for event in EVENTS:
            self.event_handlers[event].update_state(getattr(self, event))

    def on_event(self, event):
        if event not in EVENTS:
            raise ValueError(f"'event' is supposed to be one of:  {', '.join(EVENTS)}")

        def inner(func):
            self.event_handlers[event].funcs.append(func)

        return inner

    def __hash__(self) -> int:
        return self.idx

    def __str__(self):
        return f"Key(idx={self.idx}, state={self.is_pressed()})"

    def __repr__(self) -> str:
        return f"Key(idx={self.idx}, state={self.is_pressed()})"


class Pixels(Pixels):
    def set_pixel(self, idx, r, g, b):
        if isinstance(idx, int):
            idx = number_to_xy(idx, ROW_SIZE)

        y, x = idx  # axis are reversed
        self.pixelrgb(x, y, r, g, b)


class Keybow:
    """
    Represents a set of Key instances with
    associated LEDs and key behaviours.

    """

    def __init__(self, led_sleep_time=None):
        self.i2c = board.I2C()
        self._pixels = Pixels(self.i2c)

        self.keys = Matrix(*tuple(Key(idx, pin, self) for idx, pin in enumerate(_PINS)))

        self.led_sleep_time = led_sleep_time

        self.sleeping = False
        self._was_asleep = False
        self._time_of_last_press = time.monotonic()

    def update_keys(self):
        # Call this in each iteration of your while loop to update
        # to update everything's state, e.g. `keybow.update()`
        for _key in self.keys:
            _key.update()

        self._was_asleep = self.sleeping

        now = time.monotonic()

        if self.any_pressed:
            self._time_of_last_press = now

        self.sleeping = (
            not self.any_pressed
            and self.led_sleep_time is not None
            and now - self._time_of_last_press > self.led_sleep_time
        )

        if self.sleeping and not self._was_asleep:
            for _key in self.keys:
                _key.sleeping_lit = _key.lit
                _key.lit = False

        if not self.sleeping and self._was_asleep:
            for _key in self.keys:
                _key.lit = _key.sleeping_lit
                _key.sleeping_lit = False

    def update(self):
        self.update_keys()

    def set_led_color(self, idx, r: int, g: int, b: int):
        self.keys[idx].lit = (r, g, b)

    def get_states(self):
        # Returns a Boolean list of Keybow's key states
        # (0=not pressed, 1=pressed).
        return [_key.pressed for _key in self.keys]

    @property
    def pressed(self):
        return [key for key in self.keys if key.pressed]

    @property
    def not_pressed(self):
        return [key for key in self.keys if not key.pressed]

    @property
    def any_pressed(self):
        return any(self.get_states())

    def on_event(self, key_idx, event):
        return self.keys[key_idx].on_event(event)
