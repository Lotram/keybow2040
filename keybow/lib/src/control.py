import time

from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.keyboard import Keyboard


class Layer:
    def __init__(self, name, key_map, rgb):
        self.name = name
        self.key_map = key_map
        self.rgb = rgb

    def clear(self):
        pass

    def update(self):
        pass


class LayerHandler:
    def __init__(self, macro_pad):
        self.keybow = macro_pad.keybow
        self.screen = macro_pad.screen
        self.selector_gen = ((x, y) for y in range(4) for x in range(4))
        self.selector_key = self.keybow.keys[next(self.selector_gen)]
        self.selector_key.rgb = (64, 64, 64)

        self.layers = []
        self.current_layer = None

        @self.selector_key.on_event("held")
        def layer_selector(key):
            self.current_layer = None
            for _key in self.keybow.keys:
                _key.lit = False

            for layer in self.layers:
                layer.clear()

            for layer in self.layers:
                layer.selector.lit = layer.rgb

    def add_single(self, layer):
        self.layers.append(layer)
        layer.idx = len(self.layers)
        layer.selector = self.keybow.keys[next(self.selector_gen)]
        layer.keybow = self.keybow

        @layer.selector.on_event("tapped")
        def _select_layer(key):
            if not self.selector_key.held:
                return

            if not any(_key.tapped for _key in self.keybow.keys if _key != key):
                self.select_layer(layer)

    def add(self, *layers):
        for layer in layers:
            self.add_single(layer)

    def select_layer(self, layer):
        for key in set(self.keybow.keys) - {
            self.keybow.keys[idx] for idx in layer.key_map
        }:
            key.lit = False

        for key_idx in layer.key_map:
            self.keybow.keys[key_idx].lit = layer.rgb

        self.screen.show_key_map(layer.name, layer.key_map)
        self.current_layer = layer


class IRLayer(Layer):
    def __init__(self, *args, debounce=0.2, **kwargs):
        super().__init__(*args, **kwargs)
        self.debounce = debounce

    def update(self):
        now = time.monotonic()
        for key_idx, action in self.key_map.items():
            if (
                self.keybow.keys[key_idx].pressed
                and now - action.last_time_sent > self.debounce
            ):
                action.last_time_sent = now
                action.send()


class KeyboardLayer(Layer):
    def __init__(self, *args, keyboard, consumer_control, **kwargs):
        self.keyboard = keyboard
        self.consumer_control = consumer_control
        super().__init__(*args, **kwargs)

    @property
    def keycodes(self):
        return {
            action.code
            for action in self.key_map.values()
            if isinstance(action.hardware, Keyboard)
        }

    @property
    def consumer_control_codes(self):
        return {
            action.code
            for action in self.key_map.values()
            if isinstance(action.hardware, ConsumerControl)
        }

    def clear_keyboard(self):
        if any(self.keyboard.report):
            self.keyboard.release_all()

    def clear_consumer_control(self):
        if any(self.consumer_control._report):
            self.consumer_control.release()

    def clear(self):
        self.keyboard.release_all()
        self.consumer_control.release()

    def update(self):
        newly_pressed_actions = [
            action
            for key_idx, action in self.key_map.items()
            if self.keybow.keys[key_idx].newly_pressed
        ]
        if not newly_pressed_actions:
            self.clear()
            return

        keycodes_to_press = {
            action.code
            for action in newly_pressed_actions
            if isinstance(action.hardware, Keyboard)
        }

        try:
            consumer_control_code_to_press = [
                action.code
                for action in newly_pressed_actions
                if isinstance(action.hardware, ConsumerControl)
            ][0]
        except IndexError:
            consumer_control_code_to_press = None
        if consumer_control_code_to_press:
            print("consumer control", "sending", consumer_control_code_to_press)
            self.consumer_control.press(consumer_control_code_to_press)

        else:
            self.clear_consumer_control()

        if keycodes_to_press:
            print("keyboard", "sending", keycodes_to_press)
            self.keyboard.press(*keycodes_to_press)
            self.keyboard.release(*(self.keycodes - keycodes_to_press))

        else:
            self.clear_keyboard()


class Action:
    def __init__(self, hardware, code, label=""):
        self.hardware = hardware
        self.code = code
        self.label = label
        self.last_time_sent = time.monotonic()

    def send(self):
        raise NotImplementedError("You must subclass Action")

    def __str__(self) -> str:
        return f"Action(hardware={self.hardware}, code={self.code})"

    def __repr__(self) -> str:
        return f"Action(hardware={self.hardware}, code={self.code})"


class IRAction(Action):
    def send(self):
        print(self.__class__.__name__, "sending", self.code)
        self.hardware.send(self.code)


class HIDAction(Action):
    def press(self):
        self.hardware.press(self.code)

    def release(self):
        self.hardware.release(self.code)

    def send(self):
        self.press()
        self.release()
