import array

import pulseio

from .encoders.lumene import LUMENE, LUMENE_CARRIER, lumene_scancode_to_pulses
from .encoders.nec import NEC, NEC_CARRIER, NECX, nec_scancode_to_pulses
from .encoders.rc5 import RC5, RC5_CARRIER, rc5_scancode_to_pulses


class IRRemote:
    def __init__(self, pin):
        self.pin = pin

    def send(self, code):
        pulses = array.array("H", self.code_to_pulses(code))
        with pulseio.PulseOut(
            self.pin, frequency=self.frequency, duty_cycle=2**14
        ) as pulseout:
            pulseout.send(pulses)


class NECRemote(IRRemote):
    protocol = NEC
    frequency = NEC_CARRIER

    def code_to_pulses(self, code):
        return nec_scancode_to_pulses(code, self.protocol)


class NECXRemote(NECRemote):
    protocol = NECX


class RC5Remote(IRRemote):
    protocol = RC5
    frequency = RC5_CARRIER

    def code_to_pulses(self, code):
        return rc5_scancode_to_pulses(code)


class BenQ(NECXRemote):
    class Code:
        KEY_VIDEO_PREV = 0x3004  # source
        KEY_UP = 0x300B
        KEY_DOWN = 0x300C
        KEY_LEFT = 0x300D
        KEY_RIGHT = 0x300E
        KEY_ROOT_MENU = 0x300F
        MUTE = 0x3014
        KEY_OK = 0x3015
        KEY_PLAYPAUSE = 0x3021
        KEY_POWER_OFF = 0x304E
        KEY_POWER_ON = 0x304F  # ON

        VOLUME_INCREMENT = 0x3082
        VOLUME_DECREMENT = 0x3083
        BTN_BACK = 0x3085  # back menu
        KEY_BACK = 0x30A4
        KEY_FORWARD = 0x30A5
        KEY_PREVIOUSSONG = 0x30A6
        KEY_NEXTSONG = 0x30A7
        KEY_STOPCD = 0x30AA

        # others
        THREE_D = 0x308D
        PIP = 0x301B
        AUTO = 0x3008
        INVERT = 0x309D
        SWAP = 0x3012
        ECO_BLANK = 0x3007
        KEYSTONE = 0x302A
        MODE = 0x3010
        BRIGHT = 0x3016
        COLOR_MANAGE = 0x305B
        FINE_KEY_TUNE = 0x305D
        GAMMA = 0x305E
        COLOR_TEMP = 0x305F
        SHARP = 0x307E
        CONTRAST = 0x3011


class Lumene(IRRemote):
    protocol = LUMENE
    frequency = LUMENE_CARRIER

    class Code:
        STOP = 0xFDE3322
        UP = 0xFEE2221
        DOWN = 0xFBE11E0
        STEP_UP = 0xF7E2EBD
        STEP_DOWN = 0xEFE1E2C

    def code_to_pulses(self, code):
        return lumene_scancode_to_pulses(code)


class Feintech(NECRemote):
    class Code:
        OFF = 0x11F
        ON = 0x15C
        ONE = 0x11B
        TWO = 0x11A
        THREE = 0x102
        FOUR = 0x10D
        UP = 0x11E
        DOWN = 0x10A

        # Others
        _2CH = 0x112
        _5_1CH = 0x111
        PASS = 0x110
        SPDIF = 0x10E
        ARC = 0x10C
        AUTO = 0x10F

    pass


class Tangent(NECXRemote):
    class Code:
        KEY_POWER = 0x6F800
        KEY_EJECTCD = 0x6F801
        VOLUME_INCREMENT = 0x6F802
        KEY_LEFT = 0x6F803
        KEY_ENTER = 0x6F804
        KEY_RIGHT = 0x6F805
        VOLUME_DECREMENT = 0x6F806
        KEY_BLUETOOTH = 0x6F807
        KEY_SAT = 0x6F808  # DAB
        KEY_RADIO = 0x6F809
        KEY_CD = 0x6F80A
        KEY_TUNER = 0x6F80B
        KEY_AUX = 0x6F80C
        KEY_PLAYPAUSE = 0x6F80D
        KEY_INFO = 0x6F80E
        KEY_PREVIOUS = 0x6F80F
        KEY_STOP = 0x6F810
        KEY_NEXT = 0x6F811
        KEY_1 = 0x6F812
        KEY_2 = 0x6F813
        KEY_3 = 0x6F814
        KEY_4 = 0x6F815
        KEY_5 = 0x6F816
        KEY_6 = 0x6F817


class MyAmp(RC5Remote):
    class Code:
        AN1 = 0x1001
        AN2 = 0x1002
        AN3 = 0x1003
        USB = 0x1004
        OP = 0x1005
        CO = 0x1006
        bluetooth = 0x1007
        KEY_POWER = 0x100C
        MUTE = 0x100D
        VOLUME_INCREMENT = 0x1010
        VOLUME_DECREMENT = 0x1011
        BTC = 0x1038
