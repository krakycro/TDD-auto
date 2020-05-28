import ast
import re

from pathlib import Path

import general.logger as log

from general.model import *

##############################################################################

def _parse_func(file_data: dict, input_data: str, space: str = None, parent: str = None):
    functions = re.finditer(
        r"^\s*((?P<ret_val>([a-zA-Z]+\s+)*([a-zA-Z][\w:]*[\w])\s*(\<.*?\>)?)"
        r"(?P<ret_type>\s*[&*]{1,2})?\s+)?"
        r"((?P<fnc_parent>[a-zA-Z][\w:]*)::)?"
        r"(?P<fnc_name>[a-zA-Z][\w]*)\s?"
        r"\((?P<fnc_args>(\s*([a-zA-Z][\w:*&\[\], ]*)|([.]{3})\s*)*?)\)"
        r"(?P<fnc_type>\s*const)?"
        r"(?P<no_init>\s*{)",
        input_data,
        re.MULTILINE
    )
    for item in functions:
        fnc_parent = item.group("fnc_parent")
        if fnc_parent == None:
            fnc_parent = parent if parent != None else None
        elif parent != None:
            log.log_error(f"Parent {parent} clashes with {fnc_parent}")

        ret_type = item.group("ret_type")
        if ret_type == None:
            ret_type = ""

        ret_val = item.group("ret_val")
        if ret_val == None:
            ret_val = ""

        fnc_type = item.group("fnc_type")
        if fnc_type == None:
            fnc_type = ""

        fnc_args = item.group("fnc_args")
        if fnc_args == None:
            fnc_args = ""

        name = item.group("fnc_name")
        if fnc_parent != None:
            name = fnc_parent + '::' + name
        if space != None:
            name = space + '::' + name
        if name in file_data:
            continue

        key = ret_val + ' ' + name + '(' + fnc_args + ') ' + fnc_type
        file_data[key] = CObject(
            key,
            {
                "space": space,
                "ret_val": ret_val + ret_type,
                "fnc_name": item.group("fnc_name"),
                "fnc_parent": item.group("fnc_parent"),
                "fnc_args": item.group("fnc_args").strip().split(","),
                "fnc_type": item.group("fnc_type"),
            }
        )

    return True

##############################################################################

def _parse_comments(file_data: dict, input_data: str, space: str = None, parent: str = None):
    comments = re.finditer(
        r"(?P<global>.*?)?"
        r"(?P<comment>(\/\/.*?\n)|(\/\*.*?\*\/))"
        r"(?P<end>.*?\Z)",
        input_data,
        re.MULTILINE | re.DOTALL
    )
    comm_list = [comm for comm in comments]
    if len(comm_list) > 0:
        for comm in comm_list:
            _parse_func(file_data, comm.group("global"), space, parent)
            if comm.group("end") != None:
                _parse_comments(file_data, comm.group("end"), space, parent)

    else:
        _parse_func(file_data, input_data, space, parent)

    return True

##############################################################################

# TODO: in progress
def _parse_class(file_data: dict, input_data: str, space: str = None):
    classes = re.finditer(
        r"(?P<global>.*?)?"
        r"(class|struct)\s+"
        r"(?P<name>[a-zA-Z][\w]*)(\s*:\s*"
        r"(?P<parent>([a-zA-Z][\w:]*::)?[a-zA-Z][\w]*)\s?)?\s*"
        r"\{(?P<body>.*?)\};\s+//\s+(class|struct)\s+(?P=name)"
        r"(?P<end>.*?\Z)",
        input_data,
        re.MULTILINE | re.DOTALL
    )
    class_list = [is_class for is_class in classes]
    if len(class_list) > 0:
        for is_class in class_list:
            _parse_comments(file_data, is_class.group("global"), space)
            _parse_comments(file_data, is_class.group("body"), space, is_class.group("name"))
            if is_class.group("end") != None:
                _parse_class(file_data, is_class.group("end"), space)

    else:
        _parse_comments(file_data, input_data, space)

    return True

##############################################################################

def _parse_namespace(file_data: dict, input_data: str):
    namespace = re.finditer(
        r"(?P<global>.*?)?"
        r"(?P<space>namespace\s+"
        r"(?P<name>[a-zA-Z][\w]*)\s*"
        r"\{(?P<body>.*?)\}\s+//\s+namespace\s+(?P=name))"
        r"(?P<end>.*?\Z)",
        input_data,
        re.MULTILINE | re.DOTALL
    )
    space_list = [space for space in namespace]
    if len(space_list) > 0:
        for space in space_list:
            _parse_class(file_data, space.group("global"))
            _parse_class(file_data, space.group("body"), space.group("name"))
            if space.group("end") != None:
                _parse_namespace(file_data, space.group("end"))

    else:
        _parse_class(file_data, input_data)

    return True

##############################################################################

def _file_parser(args, input_data: Path):
    file_data = {}
    buffer = ""
    input_type = input_data.name.split(".")[-1]

    # TODO: add class init support withut "// class {name}"
    if input_type in ["c", "cpp", "h", "hpp"]:
        print(f"Parsing file: {input_data}")
        with open(input_data) as f:
            buffer = f.read()
        _parse_namespace(file_data, buffer)
        file_data = add_dict(args.data.objs, file_data)

    # TODO: obsolete?
    # elif input_type in ["h", "hpp"]:
    #     print(
    #         f"{input_data.name}: headers not supported, "
    #         "all data to test should be in /srcs."
    #     )

    return file_data

##############################################################################

def _dir_parser(args, parent: Path):
    for item in parent.iterdir():
        if item.is_dir():
            _dir_parser(args, item)
        elif item.is_file():
            obj = _file_parser(args, item)
            if len(obj) > 0:
                target = CFile(
                    item.name,
                    {"objects": obj}
                )
                target = add_dict(args.data.files, target)

    return True

##############################################################################

def run(args):

    if args.data != None:
        # TODO: pickle or else
        assert 1

    else:
        args.data = Bundle()

    _dir_parser(args, args.input_folder)

    return True

##############################################################################
