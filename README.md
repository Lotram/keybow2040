# Keybow 2040 macropad with IR emitter
This repo is adapted from https://github.com/manelto/MacroPad-keybow2040- and https://github.com/ntindle/Keybow2040-Macro-Pad.
In particular, I adapted the prints from https://www.printables.com/model/228327-keybow2040-macropad-with-display-and-encoder to add the IR emitter

I wrote all the python code almost from scratch, both to understand it better, and to apply personal conventions.
In particular, I implemented the NEC and RC5 IR protocols, to easily add new commands.

## Additions
In addition to all the hardware listed by the repositories above, I got a [IR emitter from Adafruit](https://www.adafruit.com/product/5639).
It needs to be soldered on the 3.3V (or 5V), GND and any other available pin. I chose the INT, since I had no use for it.

I also use a modified version of a font file found [here](https://github.com/addy-dclxvi/bitmap-font-collections) to display proper icons on the screen.

## Run on Keybow
### Libs
Copy everything from the `keybow/` dir to your device
Add the following adafruit packages:
 * adafruit_bitmap_font
 * adafruit_bus_device
 * adafruit_displayio_layout
 * adafruit_displayio_ssd1306.mpy
 * adafruit_display_text
 * adafruit_hid
 * adafruit_is31fl3731
 * adafruit_itertools
 * adafruit_midi
 * adafruit_seesaw
