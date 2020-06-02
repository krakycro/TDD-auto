import argparse
import os

from pathlib import Path

import general.logger as log

##############################################################################

def _folder_exist(dir: str):
    dir_path = Path(dir)
    if not dir_path.is_dir():
        msg = "directory does not exist: '%s'" % dir
        log.log_error(msg, error=argparse.ArgumentTypeError)

    return dir_path

##############################################################################

def arg_parser():
    parser = argparse.ArgumentParser(description='Generating TDD files.')
    parser.add_argument('-i', "--input_folder", dest="input_folder",
                        type=_folder_exist, required=True,
                        help='Input data. Mandatory field.')
    parser.add_argument('-o', "--output_folder", dest="output_folder",
                        type=Path, required=False, default=Path("temp"),
                        help='Output data. Optional field.')
    parser.add_argument('-it', "--input_type", dest='input_type',
                        type=str, default=None,
                        help=f'Text type. Default: auto')
    parser.add_argument('-ot', "--output_type", dest='output_type',
                        type=str, default=None,
                        help=f'Text type. Default: auto')
    parser.add_argument("--data", dest='data',
                        type=str, default=None,
                        help=f'Existing data to load. Default: None')
    parser.add_argument("--target_label", dest='target_label',
                        type=str, default=None,
                        help=f'Absolute label path of project. Default: None')
    parser.add_argument("--ignore_info", dest='ignore_info',
                        action='store_true', help=f'Ignore info log messages.')
    parser.add_argument("--ignore_warning", dest='ignore_warning',
                        action='store_true', help=f'Ignore warning log messages.')
    parser.add_argument("--ignore_error", dest='ignore_error',
                        action='store_true', help=f'Ignore error log messages.')
    args = parser.parse_args()

    if args.ignore_info:
        log.IGNORE_INFO = True

    if args.ignore_warning:
        log.IGNORE_WARNING = True

    if args.ignore_error:
        log.IGNORE_ERROR = True

    return args

##############################################################################