import argparse
import pathlib
from statistics import mean


def compute_avg(filepath):
    with open(filepath) as input_file:
        first_line = input_file.readline()
        signal_length = len(first_line.split("#")[0].strip().split())
        input_file.seek(0)
        result = [[] for _ in range(signal_length)]
        for line in input_file:
            values = line.split("#")[0].strip().split()
            if len(values) != signal_length:
                continue
            for idx, value in enumerate(values):
                result[idx].append(int(value))

        return [int(mean(val)) for val in result]


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filepath", type=pathlib.Path)
if __name__ == "__main__":
    args = parser.parse_args()
    print(compute_avg(args.filepath))
