import os
import re

from datetime import datetime, time
from pathlib import Path

import adapter.adapter as adapter
import general.logger as log
import generator.templates as templates

from general.model import *

##############################################################################

def _check_and_add(func: Base, target: str, target_list: list):
    if target not in target_list:
        target_list.update({target : func})

    else:
        log.log_warning(f"Duplicate: {target}")

##############################################################################

def _check_file(data: Bundle, parent: Path):
    old_list = {}
    valid_list = {}
    paths, obj_list = adapter.file_parser(parent, data.objs, parent, True)
    if len(obj_list) > 0:
        for file_id, file_val in data.files_in.items():
            for func in obj_list.values():
                key = func.fnc_args.var[1]
                if key in file_val.objects.var:
                    # log.log_info("Hit: ", key)
                    # target = file_val.objects.var[key].name.var
                    _check_and_add(func, key, valid_list)

    else:
        log.log_info(f"Empty file: {parent.name}")
        os.remove(parent)

    for func in obj_list.values():
        key = func.fnc_args.var[1]
        _check_and_add(func, key, old_list)

    old_list = dict(set(old_list.items()) - set(valid_list.items()))

    return old_list, valid_list

##############################################################################

def _dir_parser(data: Bundle, parent: Path):
    valid_list = {}
    old_list = {}
    for item in parent.iterdir():
        if item.is_dir():
            old, valid = _dir_parser(data, item)
            valid_list.update(valid)
            old_list.update(old)

        elif item.is_file():
            if item.suffix in [".c", ".cpp"]:
                old, valid = _check_file(data, item)
                valid_list.update(valid)
                old_list.update(old)

    return old_list, valid_list

##############################################################################

def _check_folder(parent: Path, project: Path, target: Path):
    if not parent.is_dir():
        parent.mkdir()

    build = Path(os.path.join(parent, "BUILD"))
    with open(build, "w") as f:
        templ = templates.get_bazel_template(project)
        f.write(templ)

    if not target.is_dir():
        target.mkdir()

    return False

##############################################################################

def _dir_generator(data: Bundle, depricated: dict, exist: dict,  parent: Path):
    for file_id, file_val in data.files_in.items():
        target = Path(os.path.join(parent, file_id + ".cpp"))
        with open(target, "w") as f:
            f.write(templates.get_cpp_include(file_val.paths.var))
            for key, obj in file_val.objects.var.items():
                if key in exist:
                    f.write(templates.get_cpp_template(exist[key], key))

                else:
                    f.write(templates.get_cpp_template(obj))

    target = Path(os.path.join(parent, "depricated.txt"))
    if len(depricated) > 0:
        with open(target, "a") as f:
            f.write(f"\nTimestamp: {datetime.now()}\n\n")
            for file_id, file_val in depricated.items():
                f.write(templates.get_cpp_template(file_val, file_id, comment = True))


##############################################################################

def run(args):
    if args.target_label == None:
        args.target_label = "//" + args.input_folder.name

    target = args.target_label.split(":")[-1]
    tests = Path(os.path.join(args.output_folder, target))

    _check_folder(args.output_folder, args.target_label, tests)

    old_list, valid_list = _dir_parser(args.data, tests)

    _dir_generator(args.data, old_list, valid_list, tests)

    return True

##############################################################################
