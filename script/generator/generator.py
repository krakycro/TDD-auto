import os
import re

from pathlib import Path

import adapter.adapter as adapter
import general.logger as log
import generator.templates as templates

from general.model import *

##############################################################################

def _check_file(data: Bundle, parent: Path):
    valid_list = {}
    obj_list = adapter.file_parser(data.objs, parent, True)
    if len(obj_list) > 0:
        for file_id, file_val in data.files_in.items():
        # TODO: only single file (cpp + h)
        #     if parent.name.split(".")[0] in file_id:
        #         print("File eq: ", parent.name, "-", file_id)
            for func in obj_list.values():
                key = func.fnc_args.var[1]
                if key in file_val.objects.var:
                    print("Hit: ", key)
                    target = file_val.objects.var[key].name.var
                    if target not in valid_list:
                        valid_list.update({target : func})
                    else:
                        print(f"Duplicate: {target} = {func}")

    else:
        print(f"Empty file: {parent.name}")

    return valid_list

##############################################################################

def _dir_parser(data: Bundle, parent: Path):
    valid_list = {}
    for item in parent.iterdir():
        if item.is_dir():
            valid_list.update(_dir_parser(data, item))

        elif item.is_file():
            valid_list.update(_check_file(data, item))

    return valid_list

##############################################################################

def _check_folder(parent: Path, name: str, tests: Path):
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

def _dir_generator(data: Bundle, exist: dict,  parent: Path):
    for file_id, file_val in data.files_in.items():
        target = Path(os.path.join(parent, file_id + ".cpp"))
        with open(target, "w") as f:
            f.write(templates.get_cpp_include())
            for key, obj in file_val.objects.var.items():
                if key in exist:
                    f.write(templates.get_cpp_template(exist[key], key))
                else:
                    f.write(templates.get_cpp_template(obj))


##############################################################################

def run(args):

    tests = Path(os.path.join(args.output_folder, "tests/"))

    _check_folder(args.output_folder, args.input_folder.name, tests)

    valid_list = _dir_parser(args.data, tests)

    _dir_generator(args.data, valid_list, tests)

    return True

##############################################################################
