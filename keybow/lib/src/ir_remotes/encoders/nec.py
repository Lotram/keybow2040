from adafruit_itertools.adafruit_itertools_extras import grouper

from .utils import IRValue, eq_margin, generate_pulses


def bitrev8(byte):
    """
    return the reverse of number, bitwise, eg
    bitrev8(3) = 192
    0b00000011 -> 0b11000000
    """
    byte = (byte >> 4) | (byte << 4)
    byte = ((byte & 0xCC) >> 2) | ((byte & 0x33) << 2)
    byte = ((byte & 0xAA) >> 1) | ((byte & 0x55) << 1)
    return byte


NEC_NBITS = 32
NEC_UNIT = 563
NEC_HEADER_PULSE = 16 * NEC_UNIT
NECX_HEADER_PULSE = 8 * NEC_UNIT
NEC_HEADER_SPACE = 8 * NEC_UNIT
NEC_REPEAT_SPACE = 4 * NEC_UNIT
NEC_BIT_PULSE = 1 * NEC_UNIT
NEC_BIT_0_SPACE = 1 * NEC_UNIT
NEC_BIT_1_SPACE = 3 * NEC_UNIT
NEC_TRAILER_PULSE = 1 * NEC_UNIT
NEC_TRAILER_SPACE = 10 * NEC_UNIT
NECX_REPEAT_BITS = 1
NEC_CARRIER = 38_000

NEC_BIT_SPACE = {"0": NEC_BIT_0_SPACE, "1": NEC_BIT_1_SPACE}

NEC32 = "NEC 32"
NECX = "NEC X"
NEC = "NEC"


def check_pulse_validity(pulses):
    assert len(pulses) == 67, "NEC codes have a length of 67"
    header_pulse, header_space = pulses[:2]
    trailer_pulse = pulses[-1]

    # assert the header pulse expected value
    assert eq_margin(header_pulse, NEC_HEADER_PULSE, NEC_UNIT / 2)

    # assert the header space expected value
    assert eq_margin(header_space, NEC_HEADER_SPACE, NEC_UNIT / 2)

    # assert the header space expected value
    assert eq_margin(trailer_pulse, NEC_TRAILER_PULSE, NEC_UNIT / 2)

    # check all pulse have the same length
    assert all(
        eq_margin(pulse, NEC_BIT_PULSE, NEC_UNIT / 2) for pulse in pulses[2:-1:2]
    )
    return True


def get_nec_bytes(bits):
    """
    get nec bytes, C style
    """

    data = int("".join(map(str, bits)), 2)

    # from https://github.com/torvalds/linux/blob/master/drivers/media/rc/ir-nec-decoder.c
    address = bitrev8((data >> 24) & 0xFF)
    not_address = bitrev8((data >> 16) & 0xFF)
    command = bitrev8((data >> 8) & 0xFF)
    not_command = bitrev8((data >> 0) & 0xFF)

    return address, not_address, command, not_command


def get_nec_bytes_2(bits):
    """
    get nec bytes, python style
    """
    bits = "".join(map(str, bits))
    nec_bytes = grouper("".join(map(str, bits)), 8)
    return [int("".join(reversed(byte)), 2) for byte in nec_bytes]


def nec_bytes_to_scancode(address, not_address, command, not_command):
    # https://github.com/torvalds/linux/blob/master/include/media/rc-core.h#L349
    if command ^ not_command != 0xFF:
        # NEC-32 protocol
        scancode = not_address << 24 | address << 16 | not_command << 8 | command

    elif address ^ not_address != 0xFF:
        # Extended NEClen
        scancode = address << 16 | not_address << 8 | command
    else:
        scancode = address << 8 | command

    return scancode


def pulses_to_scancode(pulses):
    assert check_pulse_validity(pulses)
    bits = [
        int(eq_margin(space, NEC_BIT_1_SPACE, NEC_UNIT / 2)) for space in pulses[3:-1:2]
    ]
    nec_bytes = get_nec_bytes(bits)
    return nec_bytes_to_scancode(*nec_bytes)


def nec_scancode_to_bits(scancode, protocol):
    # https://github.com/torvalds/linux/blob/master/drivers/media/rc/ir-nec-decoder.c#L176
    data = scancode & 0xFF
    if protocol == NEC32:
        addr_inv = (scancode >> 24) & 0xFF
        addr = (scancode >> 16) & 0xFF
        data_inv = (scancode >> 8) & 0xFF

    elif protocol == NECX:
        addr = (scancode >> 16) & 0xFF
        addr_inv = (scancode >> 8) & 0xFF
        data_inv = data ^ 0xFF

    else:
        addr = (scancode >> 8) & 0xFF
        addr_inv = addr ^ 0xFF
        data_inv = data ^ 0xFF

    return data_inv << 24 | data << 16 | addr_inv << 8 | addr


def nec_bits_to_pulses(data):
    return generate_pulses(
        one=IRValue(NEC_BIT_PULSE, NEC_BIT_1_SPACE),
        zero=IRValue(NEC_BIT_PULSE, NEC_BIT_0_SPACE),
        nbits=NEC_NBITS,
        data=data,
        header=IRValue(NEC_HEADER_PULSE, NEC_HEADER_SPACE),
        msb=False,
        trailer=NEC_TRAILER_PULSE,
    )


def nec_scancode_to_pulses(scancode, protocol):
    return nec_bits_to_pulses(nec_scancode_to_bits(scancode, protocol))
