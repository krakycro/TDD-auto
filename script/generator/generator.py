import os
import re

from pathlib import Path

import adapter.adapter as adapter
import general.logger as log
import generator.templates as templates

from general.model import *

##############################################################################

def _generate_folder(inputs: dict, target: dict):
    pass

##############################################################################

def _dir_parser(data: Bundle, parent: Path):
    for item in parent.iterdir():
        if item.is_dir():
            _dir_parser(data, item)
        elif item.is_file():
            obj = adapter.file_parser(data.objs, item)
            if len(obj) > 0:
                print(obj)
            
            for keys in data.files_in.keys():
                if item.name.split(".")[0] in keys:
                    print("postoji", item.name)
            
            #_generate_folder(data.files_in, obj)


    return True

##############################################################################

def _check_file(parent: Path, name: str, tests: Path):
    if not parent.is_dir():
        parent.mkdir()

    build = Path(os.path.join(parent, "BUILD"))
    with open(build, "w") as f:
        templ = templates.get_bazel_template(name)
        f.write(templ)

    if not tests.is_dir():
        tests.mkdir()

    return False

##############################################################################


def run(args):

    tests = Path(os.path.join(args.output_folder, "tests/"))
    _check_file(args.output_folder, args.input_folder.name, tests)

    _dir_parser(args.data, tests)

    return True

##############################################################################
