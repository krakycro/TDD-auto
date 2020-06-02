import ast
import os
import re
import hashlib 

from pathlib import Path

import general.logger as log

from general.model import *

##############################################################################

# TODO: add : parent{ ... } support for constructor
def _parse_func(file_data: dict, input_data: str, space: str = None, parent: str = None):
    functions = re.finditer(
        r"^\s*((?P<ret_val>([a-zA-Z]+\s+)*([a-zA-Z_][\w:]*[\w])\s*(\<.*?\>)?)"
        r"(?P<ret_type>\s*[&*]{1,2})?\s+)?"
        r"((?P<fnc_parent>[a-zA-Z_][\w:]*)::)?"
        r"(?P<fnc_name>[a-zA-Z_][\w]*)\s?"
        r"\((?P<fnc_args>(\s*([a-zA-Z_][\w:*&\[\], ]*)|([.]{3})\s*)*?)\)"
        r"(?P<fnc_type>\s*const)?"
        r"(?P<fnc_start>\s*([\w:{} ]+)?{)" # TODO: test
        r"((?P<fnc_body>.*?)}\s*\/\/\s*(?P=fnc_name))?",
        input_data,
        re.MULTILINE | re.DOTALL
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

        fnc_name = ret_val + ' ' + name + '(' + fnc_args + ') ' + fnc_type

        to_hash = hashlib.md5((ret_val + fnc_args + fnc_type).encode()).hexdigest()
        key =  re.sub(r"::", "_", name) + '_' + to_hash
        if key in file_data:
            continue

        file_data[key] = CObject(
            key,
            {
                "space": space,
                "ret_val": ret_val + ret_type,
                "fnc_name": fnc_name,
                "fnc_parent": item.group("fnc_parent"),
                "fnc_args": [item.strip() for item in item.group("fnc_args").split(",")],
                "fnc_type": item.group("fnc_type"),
                "fnc_body": item.group("fnc_body"),
            }
        )

    return True

##############################################################################

def _parse_comments(file_data: dict, input_data: str, space: str = None, parent: str = None, ignore_comms: bool = False):

    if not ignore_comms:
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
                _parse_func(file_data, comm.group("global"), space = space, parent = parent)
                if comm.group("end") != None:
                    _parse_comments(file_data, comm.group("end"), space = space, parent = parent)

        else:
            _parse_func(file_data, input_data, space, parent)

    else: 
        _parse_func(file_data, input_data, space, parent)

    return True

##############################################################################

# TODO: add class init support withut "// class {name}"
def _parse_class(file_data: dict, input_data: str, space: str = None, ignore_comms: bool = False):
    classes = re.finditer(
        r"(?P<global>.*?)?"
        r"(class|struct)\s+"
        r"(?P<name>[a-zA-Z_][\w]*)(\s*:\s*"
        r"(?P<parent>([a-zA-Z_][\w:]*::)?[a-zA-Z_][\w]*)\s?)?\s*"
        r"\{(?P<body>.*?)\};\s*\/\/\s*(class|struct)\s+(?P=name)"
        r"(?P<end>.*?\Z)",
        input_data,
        re.MULTILINE | re.DOTALL
    )
    class_list = [is_class for is_class in classes]
    if len(class_list) > 0:
        for is_class in class_list:
            _parse_comments(file_data, is_class.group("global"), space = space, ignore_comms = ignore_comms)
            _parse_comments(file_data, is_class.group("body"), space = space, parent = is_class.group("name"), ignore_comms = ignore_comms)
            if is_class.group("end") != None:
                _parse_class(file_data, is_class.group("end"), space = space, ignore_comms = ignore_comms)

    else:
        _parse_comments(file_data, input_data, space = space, ignore_comms = ignore_comms)

    return True

##############################################################################

def _parse_namespace(file_data: dict, input_data: str, ignore_comms: bool = False):
    namespace = re.finditer(
        r"(?P<global>.*?)?"
        r"(?P<space>namespace\s+"
        r"(?P<name>[a-zA-Z_][\w]*)\s*"
        r"\{(?P<body>.*?)\}\s*\/\/\s*namespace\s+(?P=name))"
        r"(?P<end>.*?\Z)",
        input_data,
        re.MULTILINE | re.DOTALL
    )
    space_list = [space for space in namespace]
    if len(space_list) > 0:
        for space in space_list:
            _parse_class(file_data, space.group("global"), ignore_comms = ignore_comms)
            _parse_class(file_data, space.group("body"), space = space.group("name"), ignore_comms = ignore_comms)
            if space.group("end") != None:
                _parse_namespace(file_data, space.group("end"), ignore_comms)

    else:
        _parse_class(file_data, input_data, ignore_comms = ignore_comms)

    return True

##############################################################################

def _parse_includes(target_name: Path, file_data: dict, input_data: str, ignore_comms: bool = False):
    paths = set()
    includes = re.finditer(
        r"(#include\s+\"(?P<local>.+?)\")|(#include\s+\<(?P<global>.+?)\>)",
        input_data,
        re.MULTILINE | re.DOTALL
    )

    path_list = [path for path in includes]
    if len(path_list) > 0:
        for path in path_list:
            if path.group("local") != None:
                paths.add(path.group("local"))

    _parse_namespace(file_data, input_data, ignore_comms)

    return paths

##############################################################################

def file_parser(root: Path, out_data: dict, input_data: Path, ignore_comms: bool = False):
    paths = set()
    file_data = {}
    buffer = ""
    input_type = input_data.suffix

    if input_type in [".c", ".cpp", ".h", ".hpp"]:
        log.log_info(f"Parsing file: {input_data}")

        try:
            relative = input_data.relative_to(root)
            if input_type in [".h", ".hpp"] and len(relative.name) > 0:
                paths.add(relative.as_posix())
        except:
            pass

        with open(input_data) as f:
            buffer = f.read()

        paths.update(_parse_includes(input_data, file_data, buffer, ignore_comms))
        file_data = add_dict(out_data, file_data)

    return paths, file_data

##############################################################################

def _dir_parser(root: Path, data: Bundle, parent: Path):
    for item in parent.iterdir():
        if item.is_dir():
            _dir_parser(root, data, item)
        elif item.is_file():
            paths, obj = file_parser(root, data.objs, item)
            if len(obj) > 0:
                target = CFile(
                    item.name.split(".")[0],
                    {
                        "paths": paths,
                        "objects": obj,
                    }
                )
                target = add_dict(data.files_in, target, merge = True)

    return True

##############################################################################

def run(args):

    if args.data != None:
        # TODO: pickle or else
        log.log_error("Not yet supported!")

    # TODO: else:
    args.data = Bundle()

    _dir_parser(args.input_folder, args.data, args.input_folder)

    return True

##############################################################################
