#!/usr/bin/env python3
# pip install pandas pyreadr

import argparse

import pyreadr


def rds_to_csv(infile, outfile):
    data = pyreadr.read_r(infile)
    keys = list(data.keys())
    assert len(keys) == 1
    desired = data[keys[0]]
    desired.to_csv(outfile)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename")
    parser.add_argument("output_filename")
    args = parser.parse_args()

    rds_to_csv(args.input_filename, args.output_filename)


if __name__ == "__main__":
    main()
