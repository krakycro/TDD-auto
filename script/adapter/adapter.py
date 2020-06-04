import ast
import os
import re
import hashlib 

from pathlib import Path

import general.logger as log

from general.model import *

##############################################################################


FUNCTION = \
{
    "cpp":
        r"^\s*((?P<ret_val>([a-zA-Z]+\s+)*([a-zA-Z_][\w:]*[\w])\s*(\<.*?\>)?)"
        r"(?P<ret_type>\s*[&*]{1,2})?\s+)?"
        r"((?P<fnc_parent>[a-zA-Z_][\w:]*)::)?"
        r"(?P<fnc_name>[a-zA-Z_][\w]*)\s?"
        r"\((?P<fnc_args>(\s*([a-zA-Z_][\w:*&\{\}\[\],=\"\' \t]*)|([.]{3})\s*)*?)\)"
        r"(?P<fnc_type>\s*const)?"
        r"(?P<fnc_start>\s*([\w:{}() \t]+)?{)" # TODO: test
        r"((?P<fnc_body>.*?)}\s*\/\/\s*(?P=fnc_name))?",
    "py":
        r"def([ \t]|(\\\n))+(?P<fnc_name>[a-zA-Z_][\w]*)([ \t]|(\\\n))?"
        r"\((?P<fnc_args>(\s*[a-zA-Z_*][\w:\{\}\[\],=*&\"\' \t]*\s*)*?)\)"
        r"([ \t]|(\\\n))*:[ \t]*\n+(?P<ident>[ \t]+)" # removed (?=\w)
        r"(?P<fnc_body>(.*\n+(?P=ident))*.*\n)"
        r"(?P<ret_val>\Z^)?"
        r"(?P<fnc_parent>\Z^)?"
        r"(?P<ret_type>\Z^)?"
        r"(?P<fnc_type>\Z^)?"
        r"(?P<fnc_start>\Z^)?",
}

FUNCTION_FLAGS = \
{
    "cpp": re.MULTILINE | re.DOTALL,
    "py": re.MULTILINE,
}

COMMENT = \
{
    "cpp":
        r"(?P<comment>(\/\/.*?\n)|(\/\*.*?\*\/))",
    "py":
        r"(?P<comment>(#.*?\n)|((\'|\"){3}.*?(\'|\"){3}))",
}

CLASS = \
{
    "cpp":
        r"(class|struct)\s+"
        r"(?P<name>[a-zA-Z_][\w]*)(\s*:\s*"
        r"(?P<parent>([a-zA-Z_][\w:]*::)?[a-zA-Z_][\w]*)\s?)?\s*"
        r"\{(?P<body>.*?)\};\s*\/\/\s*(class|struct)\s+(?P=name)",
    "py":
        r"class([ \t]|(\\\n))+"
        r"(?P<name>[a-zA-Z_][\w]*)([ \t]|(\\\n))*"
        r"(?P<parent>\((\s*([a-zA-Z_][\w, \t]*)\s*)*?\))?"
        r"([ \t]|(\\\n))*:[ \t]*\n+(?P<ident>[ \t]+)" # removed (?=\w)
        r"(?P<body>(.*\n+(?P=ident))*.*\n)",
}

CLASS_FLAGS = \
{
    "cpp": re.MULTILINE | re.DOTALL,
    "py": re.MULTILINE,
}

NAMESPACE = \
{
    "cpp":
        r"(?P<space>namespace\s+"
        r"(?P<name>[a-zA-Z_][\w]*)\s*"
        r"\{(?P<body>.*?)\}\s*\/\/\s*namespace\s+(?P=name))",
    "py":
        r"(?P<end>.*?\Z)?"
        r"(?P<space>\Z^)?"
        r"(?P<name>\Z^)?",
}

INCLUDE = \
{
    "cpp":
        r"(#include\s+\"(?P<local>.+?)\")|(#include\s+\<(?P<global>.+?)\>)",
    "py":
        r"(?P<global>(from\s+[a-zA-Z_][\w.]*\s+)?(import)\s+[a-zA-Z_*][\w.]*)(\s+as\s+[a-zA-Z_][\w.]*)?"
        r"(?P<local>\Z^)?",
}


##############################################################################

def _parse_func(types: str, file_data: dict, input_data: str, space: str = None, parent: str = None):
    functions = re.finditer(
        FUNCTION[types],
        input_data,
        FUNCTION_FLAGS[types]
    )
    item_list = [item for item in functions]
    if len(item_list) > 0:
        for item in item_list:
            fnc_parent = item.group("fnc_parent")
            if fnc_parent == None or len(fnc_parent) == 0:
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

def _parse_comments(types: str, file_data: dict, input_data: str, space: str = None, parent: str = None, use_class = False):
    input_data = re.sub(
        COMMENT[types],
        "",
        input_data,
        flags = re.MULTILINE | re.DOTALL
    )

    if use_class:
        _parse_class(types, file_data, input_data, space = space, parent = parent, ignore_comms = True)

    else:
        _parse_func(types, file_data, input_data, space = space, parent = parent)

    return True

##############################################################################

# TODO: add cpp class init support without "// class {name}"
def _parse_class(types: str, file_data: dict, input_data: str, space: str = None, parent: str = None, ignore_comms: bool = False):
    classes = re.finditer(
        CLASS[types],
        input_data,
        CLASS_FLAGS[types]
    )
    class_list = [is_class for is_class in classes]
    if len(class_list) > 0:

        glob = input_data[0:class_list[0].start()]
        if ignore_comms:
            _parse_func(types, file_data, glob, space = space, parent = parent)

        else:
            _parse_comments(types, file_data, glob, space = space, parent = parent)

        for is_class in class_list:
            new_parent = is_class.group("name")
            if parent != None:
                new_parent = parent + "::" + is_class.group("name")

            _parse_class(types, file_data, is_class.group("body"), space = space, parent = new_parent, ignore_comms = ignore_comms)

        end = input_data[class_list[-1].end():]
        _parse_class(types, file_data, end, space = space, parent = parent, ignore_comms = ignore_comms)

    else:
        if ignore_comms:
            _parse_func(types, file_data, input_data, space = space, parent = parent)

        else:
            _parse_comments(types, file_data, input_data, space = space, parent = parent)

    return True

##############################################################################

def _parse_namespace(types: str, file_data: dict, input_data: str, ignore_comms: bool = False):
    namespace = re.finditer(
        NAMESPACE[types],
        input_data,
        re.MULTILINE | re.DOTALL
    )
    space_list = [space for space in namespace]
    if len(space_list) > 0:

        glob = input_data[0:space_list[0].start()]
        _parse_class(types, file_data, glob, ignore_comms = ignore_comms)

        for space in space_list:
            _parse_class(types, file_data, space.group("body"), space = space.group("name"), ignore_comms = ignore_comms)

        end = input_data[space_list[-1].end():]
        _parse_class(types, file_data, end, ignore_comms = ignore_comms)

    else:
        _parse_class(types, file_data, input_data, ignore_comms = ignore_comms)

    return True

##############################################################################

def _parse_includes(types: str, target_name: Path, file_data: dict, input_data: str, ignore_comms: bool = False):
    paths = set()
    includes = re.finditer(
        INCLUDE[types],
        input_data,
        re.MULTILINE | re.DOTALL
    )

    path_list = [path for path in includes]
    if len(path_list) > 0:
        for path in path_list:
            if path.group("local") != None:
                paths.add(path.group("local"))

    if types in log.TYPE_LIST_PY:
        _parse_comments(types, file_data, input_data, use_class = True)

    else:
        _parse_namespace(types, file_data, input_data, ignore_comms)

    return paths

##############################################################################

def file_parser(types: str, root: Path, out_data: dict, input_data: Path, ignore_comms: bool = False):
    paths = set()
    file_data = {}
    buffer = ""
    input_type = input_data.suffix[1:]

    if types in log.TYPE_LIST_C + log.TYPE_LIST_PY:
        if input_type in log.TYPE_LIST_C + log.TYPE_LIST_PY:
            log.log_info(f"Parsing file: {input_data}")

            try:
                relative = input_data.relative_to(root)
                if input_type in ["h", "hpp", "py"] and len(relative.name) > 0:
                    paths.add(relative.as_posix())
            except:
                pass

            with open(input_data) as f:
                buffer = f.read()

            paths.update(_parse_includes(types, input_data, file_data, buffer, ignore_comms))
            file_data = add_dict(out_data, file_data)

    else:
        log.log_info(f"Unknown type: {types}")

    return paths, file_data

##############################################################################

def _dir_parser(root: Path, data: Bundle, parent: Path):
    for item in parent.iterdir():
        if item.is_dir():
            _dir_parser(root, data, item)
        elif item.is_file():
            if len(item.suffix) > 0 and data.ptype == None:
                data.ptype = item.suffix[1:]
                if data.ptype in log.TYPE_LIST_C:
                    data.ptype = "cpp"

                elif data.ptype in log.TYPE_LIST_PY:
                    data.ptype = "py"

            paths, obj = file_parser(data.ptype, root, data.objs, item)
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

    args.data.ptype = args.input_type

    _dir_parser(args.input_folder, args.data, args.input_folder)

    return True

##############################################################################
