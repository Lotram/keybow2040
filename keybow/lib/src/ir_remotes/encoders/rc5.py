from adafruit_itertools import chain_from_iterable, groupby

from .utils import eq_margin


# https://github.com/torvalds/linux/blob/master/drivers/media/rc/ir-rc5-decoder.c
RC5 = "rc5"
RC5_NBITS = 14
RC5_SZ_NBITS = 15
RC5X_NBITS = 20
CHECK_RC5X_NBITS = 8
RC5_UNIT = 889
RC5_BIT_START = 1 * RC5_UNIT
RC5_BIT_END = 1 * RC5_UNIT
RC5X_SPACE = 4 * RC5_UNIT
RC5_TRAILER = 6 * RC5_UNIT  # actually 50 times
RC5_CARRIER = 36_000


def pulses_to_scancode(pulses):

    half_bits = list(
        chain_from_iterable(
            [1 if i % 2 == 0 else -1]
            * (1 if eq_margin(pulse, RC5_UNIT, RC5_UNIT / 2) else 2)
            for i, pulse in enumerate(pulses)
        )
    )
    half_bits.insert(0, -1)
    if len(half_bits) < 28:
        half_bits.append(-1)

    assert len(half_bits) == 28

    bits = [int(bool(1 - half_bit)) for half_bit in half_bits[::2]]

    # First two bits are supposed to bo 1
    assert bits[0] == 1
    assert bits[1] == 1

    bit_string = "".join(map(str, bits))
    address = bit_string[3:8]
    command = bit_string[8:]
    return [int(val, 2).to_bytes(1, "big") for val in (address, command)]


def rc5_scancode_to_pulses(scancode, reverse_bit=False):
    address, command = scancode.to_bytes(2, "big")
    bit_string = f"11{int(reverse_bit)}{address:05b}{command:06b}"
    assert len(bit_string) == 14
    half_bits = list(
        chain_from_iterable((-1, 1) if int(bit) else (1, -1) for bit in bit_string)
    )
    pulses = [sum(group) * RC5_UNIT for _, group in groupby(half_bits)]
    assert pulses[0] < 0
    assert pulses[1] > 0
    pulses = pulses[1:]
    if pulses[-1] < 0:
        pulses = pulses[:-1]
    return list(map(abs, pulses))
