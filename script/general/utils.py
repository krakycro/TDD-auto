import argparse
import os

from pathlib import Path

import general.logger as log

##############################################################################

def _folder_exist(dirs: str):
    dir_path = Path(dirs)
    if not dir_path.is_dir():
        msg = "directory does not exist: '%s'" % dir
        log.log_error(msg, error=argparse.ArgumentTypeError)

    return dir_path

##############################################################################

def _is_correct_type(dirs: str):
    if dirs not in log.TYPE_LIST_C + log.TYPE_LIST_PY:
        msg = "Type does not exist: '%s'" % dir
        log.log_error(msg, error=argparse.ArgumentTypeError)

    return dirs

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
                        type=_is_correct_type, default=None,
                        help=f'Text type. Default: auto')
    parser.add_argument("--data", dest='data',
                        type=str, default=None,
                        help=f'Existing data to load. Default: None')
    parser.add_argument("--target_label", dest='target_label',
                        type=str, default=None,
                        help=f'Absolute label path of project. Default: None')
    parser.add_argument("--gtest_name", dest='gtest_name',
                        type=str, default="gtest",
                        help=f'Name of gtest workspace. Default: gtest')
    parser.add_argument("--ignore_info", dest='ignore_info',
                        action='store_true', help=f'Ignore info log messages.')
    parser.add_argument("--ignore_warning", dest='ignore_warning',
                        action='store_true', help=f'Ignore warning log messages.')
    parser.add_argument("--ignore_error", dest='ignore_error',
                        action='store_true', help=f'Ignore error log messages.')
    args = parser.parse_args()

    log.log_setting(args)

    return args

##############################################################################