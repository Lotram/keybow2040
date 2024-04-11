import re
import subprocess


def parse_line(line: str):
    match = re.match(r"[^#]*(?=\ #)", line)
    if match is None:
        return
    pulses = match.group().split()
    if len(pulses) < 10:
        return

    return " ".join(pulses)


def run_ir_ctl():
    proc = subprocess.Popen(
        "ir-ctl -d /dev/lirc1 -r", shell=True, stdout=subprocess.PIPE
    )
    try:
        for line in iter(proc.stdout.readline, ""):
            pulses = parse_line(line.decode())
            if pulses is not None:
                print(pulses)
    except KeyboardInterrupt:
        return
