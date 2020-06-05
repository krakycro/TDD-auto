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

def _check_file(types: str, data: Bundle, parent: Path):
    old_list = {}
    valid_list = {}
    paths, obj_list = adapter.file_parser(types, parent, data.objs, parent, ignore_comms = True)
    if len(obj_list) > 0:
        for file_id, file_val in data.files_in.items():
            for func in obj_list.values():
                if types in log.TYPE_LIST_C:
                    if len(func.fnc_args.var) < 2:
                        log.log_warning(f"Missing second arg: {func.fnc_args}")

                    key = func.fnc_args.var[1].split(" ")[0]

                elif types in log.TYPE_LIST_PY:
                    key = re.search(r"test_(?P<name>.*?)\(", func.fnc_name.var).group("name")

                if key in file_val.objects.var:
                    # log.log_info("Hit: ", key)
                    # target = file_val.objects.var[key].name.var
                    _check_and_add(func, key, valid_list)

    else:
        log.log_info(f"Empty file: {parent.name}")
        os.remove(parent)

    for func in obj_list.values():
        if types in log.TYPE_LIST_C:
            key = func.fnc_args.var[1].split(" ")[0]

        elif types in log.TYPE_LIST_PY:
            key = re.search(r"test_(?P<name>.*?)\(", func.fnc_name.var).group("name")

        _check_and_add(func, key, old_list)

    old_list = dict(set(old_list.items()) - set(valid_list.items()))

    return old_list, valid_list

##############################################################################

def _dir_parser(data: Bundle, parent: Path, types: str):
    valid_list = {}
    old_list = {}
    for item in parent.iterdir():
        if item.is_dir():
            old, valid = _dir_parser(data, item, types)
            valid_list.update(valid)
            old_list.update(old)

        elif item.is_file():
            if item.suffix[1:] in [types]:
                old, valid = _check_file(types, data, item)
                valid_list.update(valid)
                old_list.update(old)

    return old_list, valid_list

##############################################################################

def _check_folder(args, parent: Path, project: Path, target: str, test: Path):
    if not parent.is_dir():
        parent.mkdir()

    templ = ""
    build = Path(os.path.join(parent, "BUILD"))
    if args.data.ptype in log.TYPE_LIST_C:
        templ = templates.get_bazel_cpp_template(args, project)

    elif args.data.ptype in log.TYPE_LIST_PY:
        templ = templates.get_bazel_py_template(args, project)

    with open(build, "w") as f:
        f.write(templ)

    if not test.is_dir():
        test.mkdir()

    return False

##############################################################################

def _main_parser(args, parent: Path, target: str):
    if args.data.ptype in log.TYPE_LIST_C:
        pass
    elif args.data.ptype in log.TYPE_LIST_PY:
        import_list = set()
        for name, files in args.data.files_in.items():
            tmp = target + "." + name
            tmp = re.sub(r"/", ".", tmp)
            import_list.add(tmp)

        build = Path(os.path.join(parent, target + "_unit_test.py"))
        with open(build, "w") as f:
            f.write(templates.get_py_main(args, import_list))

##############################################################################

def _dir_generator(args, depricated: dict, exist: dict,  parent: Path):
    for file_id, file_val in args.data.files_in.items():
        target = Path(os.path.join(parent, file_id + "." + args.data.ptype))
        with open(target, "w") as f:
            if args.data.ptype in log.TYPE_LIST_C:
                f.write(templates.get_cpp_include(args, file_val.paths.var))

            elif args.data.ptype in log.TYPE_LIST_PY:
                import_list = set()
                for name in file_val.paths.var:
                    tmp = parent.name + "." + file_id
                    import_list.add(tmp)

                f.write(templates.get_py_import(args, import_list))
                f.write(templates.get_py_class(args, file_id))

            for key, obj in file_val.objects.var.items():
                if key in exist:
                    if args.data.ptype in log.TYPE_LIST_C:
                        f.write(templates.get_cpp_template(args, exist[key], key))

                    elif args.data.ptype in log.TYPE_LIST_PY:
                        f.write(templates.get_py_template(args, exist[key], key))

                else:
                    if args.data.ptype in log.TYPE_LIST_C:
                        f.write(templates.get_cpp_template(args, obj))

                    elif args.data.ptype in log.TYPE_LIST_PY:
                        f.write(templates.get_py_template(args, obj))

    target = Path(os.path.join(parent, "depricated.txt"))
    if len(depricated) > 0:
        with open(target, "a") as f:
            f.write(f"\nTimestamp: {datetime.now()}\n\n")
            for file_id, file_val in depricated.items():
                if args.data.ptype in log.TYPE_LIST_C:
                    f.write(templates.get_cpp_template(args, file_val, file_id, comment = True))

                if args.data.ptype in log.TYPE_LIST_PY:
                    f.write(templates.get_py_template(args, file_val, file_id, comment = True))

##############################################################################

def run(args):
    if args.data.ptype in log.TYPE_LIST_C + log.TYPE_LIST_PY:
        if args.target_label == None:
            args.target_label = "//" + args.input_folder.name

        target = args.target_label.split(":")[-1].split("//")[-1]
        tests = Path(os.path.join(args.output_folder, target))

        _check_folder(args, args.output_folder, args.target_label, target, tests)
        old_list, valid_list = _dir_parser(args.data, tests, args.data.ptype)
        _main_parser(args, args.output_folder, target)

        _dir_generator(args, old_list, valid_list, tests)

    else:
        log.log_warning(f"No support for generating {args.data.ptype}!")

    return True

##############################################################################
