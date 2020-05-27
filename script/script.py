import argparse
import os

from pathlib import Path

from general.model import *
import general.logger as log
import adapter.adapter as adapter
import adapter.linker as linker


def _folder_exist(dir: str):
    dir_path = Path(dir)
    if not dir_path.is_dir():
        msg = "directory does not exist: '%s'" % dir
        log.log_error(msg, error=argparse.ArgumentTypeError)

    return dir_path


def arg_parser():
    parser = argparse.ArgumentParser(description='Generating TDD files.')
    parser.add_argument('-i', "--input_folder", dest="input_folder",
                        type=_folder_exist, required=True,
                        help='Input data. Mandatory field.')
    parser.add_argument('-o', "--output_folder", dest="output_folder",
                        type=Path, required=False, default="temp",
                        help='Output data. Optional field.')
    parser.add_argument('-ti', "--input_type", dest='input_type',
                        type=str, default=None,
                        help=f'Text type (json, c). Default: auto')
    parser.add_argument('-to', "--output_type", dest='output_type',
                        type=str, default=None,
                        help=f'Text type (c, h, a2l, generic_a2l, gdb, '
                        f'params, dcm, generic_dcm). Default: auto')
    parser.add_argument("--data", dest='data',
                        type=str, default=None,
                        help=f'Existing data to load. Default: None')
    args = parser.parse_args()

    return args


def main():

    args = arg_parser()

    adapter.run(args)

    linker.run(args)

    return 0


if __name__ == "__main__":
    exit(main())