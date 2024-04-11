import board
from adafruit_itertools import chain_from_iterable
from src.config import layers
from src.control import LayerHandler
from src.keybow import Keybow
from src.screen import Screen


class MacroPad:
    def __init__(self) -> None:
        self.i2c = board.I2C()
        self.keybow = Keybow(led_sleep_time=5)
        self.screen = Screen(128, 64, self.i2c)
        self.layer_handler = LayerHandler(self)
        self.layer_handler.add(*layers)
        self.init_glyphs()

    def init_glyphs(self):
        # ensure all glyphs are already loaded
        chars = set(
            chain_from_iterable(
                action.label
                for layer in self.layer_handler.layers
                for action in layer.key_map.values()
            )
        )
        self.screen.load_glyphs(chars)

    def handle_error(self):
        for key in self.keybow.keys:
            key.lit = (255, 0, 0)

    def update_layer(self):
        handler = self.layer_handler
        if handler.selector_key.held:
            return

        # trigger actions depending on the layer
        if handler.current_layer is not None:
            handler.current_layer.update()

        elif not self.keybow.sleeping:
            handler.selector_key.lit = True

    def update(self):
        try:
            self.keybow.update()
            self.update_layer()

        except Exception:
            self.handle_error()
            raise
