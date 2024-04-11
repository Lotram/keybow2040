from .utils import IRValue, decode_bits, generate_pulses


LUMENE = "lumene"
LUMENE_UNIT = 417
LUMENE_GAP = 50 * LUMENE_UNIT
LUMENE_CARRIER = 38_000

LUMENE_NBITS = 32
LUMENE_HEADER_PULSE = None
LUMENE_HEADER_SPACE = None
LUMENE_BIT_0_PULSE = 3 * LUMENE_UNIT
LUMENE_BIT_1_PULSE = 1 * LUMENE_UNIT
LUMENE_BIT_0_SPACE = 1 * LUMENE_UNIT
LUMENE_BIT_1_SPACE = 3 * LUMENE_UNIT

LUMENE_BIT_1 = IRValue(LUMENE_BIT_1_PULSE, LUMENE_BIT_1_SPACE)
LUMENE_BIT_0 = IRValue(LUMENE_BIT_0_PULSE, LUMENE_BIT_0_SPACE)


def pulses_to_lumene_code(pulses):
    bit_array = decode_bits(
        pulses,
        one=LUMENE_BIT_1,
        zero=LUMENE_BIT_0,
        has_trail=False,
    )
    bits = "".join(map(str, bit_array))
    return hex(int(bits, 2))


def lumene_scancode_to_pulses(scancode):
    return generate_pulses(one=LUMENE_BIT_1, zero=LUMENE_BIT_0, nbits=32, data=scancode)
