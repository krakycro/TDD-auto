import ast
import re

from general.model import *
import general.logger as log
from pathlib import Path


def _parse_func(file_data: dict, buffer: str, space: str = None):
    functions = re.finditer(
        r"^\s*(?P<ret_val>([a-zA-Z]+\s+)*([a-zA-Z][\w:]*)\s*(\<.*?\>)?)(?P<ret_type>\s*[&*]{1,2})?\s+"
        r"(?P<fnc_name>[a-zA-Z][\w]*)\s?\((?P<fnc_args>.*?)\)(?P<fnc_type>\s*const)?",
        buffer,
        re.MULTILINE
    )
    for item in functions:
        name = item.group("fnc_name")
        if space != None:
            name = space + '_' + name
        if name in file_data:
            continue
        ret_type = item.group("ret_type")
        if ret_type == None:
            ret_type = ""
        file_data[name] = CObject(
            item.group("fnc_name"),
            {
                "space": space,
                "ret_val": item.group("ret_val") + ret_type,
                "fnc_args": item.group("fnc_args").strip().split(","),
                "fnc_type": item.group("fnc_type"),
            }
        )

    return True


def _parse_c(file_data: dict, file_path: Path, input_data: str):
    namespace = re.finditer(
        r"(?P<global>.*?)?(?P<space>namespace\s+(?P<name>[a-zA-Z][\w]*)\s*"
        r"\{(?P<body>.*?)\}\s+//\s+namespace\s+(?P=name))(?P<end>.*?\Z)",
        input_data,
        re.MULTILINE | re.DOTALL
    )
    space_list = [space for space in namespace]
    if len(space_list) > 0:
        for space in space_list:
            _parse_func(file_data, space.group("global"))
            _parse_func(file_data, space.group("body"), space.group("name"))
            if space.group("end") != None:
                _parse_c(file_data, file_path, space.group("end"))

    else:
        _parse_func(file_data, input_data)

    return True


def _file_parser(args, input_data: Path):
    file_data = {}
    buffer = ""
    input_type = input_data.name.split(".")[-1]

    if input_type in ["c", "cpp", "h", "hpp"]:
        print(f"Parsing file: {input_data}")
        with open(input_data) as f:
            buffer = f.read()
        _parse_c(file_data, input_data, buffer)

    file_data = add_dict(args.data.objs, file_data)

    return file_data


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


def run(args):

    if args.data != None:
        # todo: pickle or else
        assert 1

    else:
        args.data = Bundle()

    _dir_parser(args, args.input_folder)

    return True
