import adafruit_displayio_ssd1306
import displayio
import terminalio
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label, wrap_text_to_lines
from adafruit_displayio_layout.layouts.grid_layout import GridLayout
from src.utils import number_to_xy

FONT_FILE = "lib/waffle-10.bdf"


class Screen:
    def _init_font(self):
        # load bitmap font with symbols, and merge it with default font
        try:
            self.font = bitmap_font.load_font(FONT_FILE)
        except OSError:
            print(f"{FONT_FILE} does not exist")
            self.font = terminalio.FONT
            return

        # printable chars
        glyphs = {
            chr_idx: terminalio.FONT.get_glyph(chr_idx) for chr_idx in range(32, 127)
        }
        self.font._glyphs.update(glyphs)

    def load_glyphs(self, chars):
        self.font.load_glyphs([ord(char) for char in chars])

    def __init__(self, width, height, i2c, address=0x3D):
        # Initalize the display
        displayio.release_displays()
        self.width = width
        self.height = height
        self.display = adafruit_displayio_ssd1306.SSD1306(
            displayio.I2CDisplay(i2c, device_address=address),
            width=self.width,
            height=self.height,
        )
        self._init_font()

    def print(self, text: str):
        # Make the display context
        splash = displayio.Group()
        self.display.show(splash)

        color_bitmap = displayio.Bitmap(self.width, self.height, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = 0xFFFFFF

        bg_sprite = displayio.TileGrid(
            color_bitmap, pixel_shader=color_palette, x=0, y=0
        )
        splash.append(bg_sprite)

        # Draw a smaller inner rectangle
        inner_bitmap = displayio.Bitmap(self.width - 10, self.height - 10, 1)
        inner_palette = displayio.Palette(1)
        inner_palette[0] = 0x000000  # Black
        inner_sprite = displayio.TileGrid(
            inner_bitmap, pixel_shader=inner_palette, x=5, y=4
        )
        splash.append(inner_sprite)

        text = "\n".join(wrap_text_to_lines(text, 15))

        text_area = label.Label(self.font, text=text, x=28, y=15)
        splash.append(text_area)

    def clear(self):
        splash = displayio.Group()
        self.display.show(splash)

    def show_grid(self, content, title=None, size=4):
        main_group = displayio.Group()
        self.display.show(main_group)
        title_width = 16
        if title:
            title_area = label.Label(
                self.font,
                text=title,
                anchor_point=(0, 1),
                anchored_position=(1, self.height),
                label_direction="UPR",
            )
            main_group.append(title_area)

            layout_width = self.width - title_width
            layout_x = title_width
        else:
            layout_width = self.width
            layout_x = title_width

        layout = GridLayout(
            x=layout_x,
            y=0,
            width=layout_width,
            height=self.height,
            grid_size=(size, size),
            cell_padding=1,
            divider_lines=True,
            cell_anchor_point=(0.5, 0.5),
        )

        labels = [
            label.Label(self.font, cell_anchor_point=(0.5, 0.5), text=label_)
            for label_ in content
        ]

        for idx in range(len(labels)):
            label_ = labels[idx]
            x, y = number_to_xy(idx, size)
            layout.add_content(
                label_, grid_position=(x, size - 1 - y), cell_size=(1, 1)
            )

        main_group.append(layout)

    def show_key_map(self, title, key_map):
        labels = []
        for i in range(4):
            for j in range(4):
                if (i, j) in key_map:
                    labels.append(key_map.get((i, j)).label)
                else:
                    labels.append(" ")
        self.show_grid(labels, title=title or None)
