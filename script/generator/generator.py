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
    paths, obj_list = adapter.file_parser(parent, data.objs, parent, True)
    if len(obj_list) > 0:
        for file_id, file_val in data.files_in.items():
        # TODO: only single file (cpp + h)
        #     if parent.name.split(".")[0] in file_id:
        #         log.log_info("File eq: ", parent.name, "-", file_id)
            for func in obj_list.values():
                key = func.fnc_args.var[1]
                if key in file_val.objects.var:
                    log.log_info("Hit: ", key)
                    target = file_val.objects.var[key].name.var
                    if target not in valid_list:
                        valid_list.update({target : func})
                    else:
                        log.log_warning(f"Duplicate: {target} = {func}")

    else:
        log.log_info(f"Empty file: {parent.name}")

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

def _dir_generator(data: Bundle, exist: dict,  parent: Path):
    for file_id, file_val in data.files_in.items():
        target = Path(os.path.join(parent, file_id + ".cpp"))
        with open(target, "w") as f:
            f.write(templates.get_cpp_include(file_val.paths.var))
            for key, obj in file_val.objects.var.items():
                if key in exist:
                    f.write(templates.get_cpp_template(exist[key], key))
                else:
                    f.write(templates.get_cpp_template(obj))


##############################################################################

def run(args):
    if args.target_label == None:
        args.target_label = "//" + args.input_folder.name

    target = args.target_label.split(":")[-1]
    tests = Path(os.path.join(args.output_folder, target))

    _check_folder(args.output_folder, args.target_label, tests)

    valid_list = _dir_parser(args.data, tests)

    _dir_generator(args.data, valid_list, tests)

    return True

##############################################################################
