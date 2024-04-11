from collections import namedtuple


try:
    from ulab import numpy
except ModuleNotFoundError:
    import numpy

from adafruit_itertools import chain_from_iterable
from adafruit_itertools.adafruit_itertools_extras import grouper


IRValue = namedtuple("IRValue", ["mark", "space"])


class IRDecodeException(Exception):
    """Generic decode exception"""


def eq_margin(value: int, target: int, margin: float) -> bool:
    """
    return whether a value is close to a target, by a margin
    """
    return target - margin <= value <= target + margin


def eq_margin_bit(
    bit: tuple[int, int], target_bit: tuple[int, int], margin: int
) -> bool:
    return all(eq_margin(bit[i], target_bit[i], margin) for i in (0, 1))


def parse_ir_ctl_string(raw: str) -> list[int]:
    return [int(raw_pulse[1:]) for raw_pulse in raw.split()]


def find_lengths(pulses: list[int]) -> dict[int, int]:
    lengths = {pulses[0]: [pulses[0]]}
    for pulse in pulses[1:]:
        if any(
            eq_margin(pulse, pulse_length := length, length * 0.1) for length in lengths
        ):
            values = lengths.pop(pulse_length)
            values.append(pulse)

            new_mean = round(numpy.mean(values))
            lengths[new_mean] = values
        else:
            lengths[pulse] = [pulse]

    return {length: len(pulses) for length, pulsees in lengths.items()}


def generate_pulses(
    one: IRValue,
    zero: IRValue,
    nbits: int,
    data: int,
    header: IRValue | None = None,
    trailer: int = 0,
    msb: bool = True,
):
    bit_string = "{number:0{width}b}".format(width=nbits, number=data)

    if not msb:
        # circuitpython does not support ""[::-1]
        bit_string = "".join(reversed(bit_string))

    bits = [bool(int(bit)) for bit in bit_string]
    pulses = []
    if header and header.mark:
        pulses = list(header)

    pulses.extend(chain_from_iterable(one if bit else zero for bit in bits))

    if trailer:
        pulses.append(trailer)

    return pulses


def get_theoretical_bit(
    two_pulses: tuple[int, int], lengths: list[int]
) -> tuple[int, int]:
    unit = min(lengths)
    return tuple(
        next(length for length in lengths if eq_margin(pulse, length, unit / 2))
        for pulse in two_pulses
    )


def decode_bits(
    pulses: list[int],
    one: tuple[int, int] | None = None,
    zero: tuple[int, int] | None = None,
    first_bit_value=1,
    has_trail=True,
) -> list[int]:
    assert (one is None) == (zero is None)
    pulses = pulses.copy()
    if len(pulses) % 2 == 1:
        if has_trail:
            pulses = pulses[:-1]

    lengths = find_lengths(pulses)

    # remove outliers
    valid_lengths = [length for length, count in lengths.items() if count > 1]

    unit = min(lengths)

    # remove outliers (possibly the header)
    pulses = [
        pulse
        for pulse in pulses
        if any(
            eq_margin(pulse, valid_length, unit // 2) for valid_length in valid_lengths
        )
    ]

    first_bit = get_theoretical_bit(tuple(pulses[:2]), valid_lengths)
    if one is None:
        other_bit = None
    else:
        first_bit_value = 1 if eq_margin_bit(first_bit, one, unit // 2) else 0
        other_bit = zero if first_bit_value == 1 else one

    bits = [first_bit_value]

    for bit in grouper(pulses[2::], 2):
        # last space may not have been registered
        if bit[1] is None:
            assert other_bit is not None
            bits.append(
                first_bit_value
                if eq_margin(bit[0], first_bit[0], unit // 2)
                else 1 - first_bit_value
            )

        elif eq_margin_bit(bit, first_bit, unit // 2):
            bits.append(first_bit_value)
        elif other_bit is None:
            other_bit = get_theoretical_bit(bit, valid_lengths)
            bits.append(1 - first_bit_value)

        elif eq_margin_bit(bit, other_bit, unit // 2):
            bits.append(1 - first_bit_value)

        else:
            print("first_bit", first_bit)
            print("other_bit", other_bit)
            print("third_bit", get_theoretical_bit(bit, valid_lengths))
            raise IRDecodeException("more than 2 types of bits detected")

    return bits
