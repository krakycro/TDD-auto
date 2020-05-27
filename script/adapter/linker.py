import re

from general.model import *
import general.logger as log
from pathlib import Path

def _get_var_obj(value):
    if isinstance(value, str) and len(value) > 0:
        var_name = re.sub(
            r"\s+(inline)|(constexpr)|(static)\s+",
            "",
            value,
            re.MULTILINE
        )
        var_name = re.sub(r"(\s*const\s+)|( )", "", var_name, re.MULTILINE)

        is_const = re.search(r"\s*const\s+", var_name, re.MULTILINE)
        if is_const != None:
            is_const = True
            var_name = "const " + var_name

        else:
            is_const = False

        var_type = re.search(r"\s*[*&]{1,2}\Z", var_name, re.MULTILINE)
        var_type = var_type.group(0) if var_type != None else None
        value = CDataType(
            var_name,
            {
                "is_const": is_const,
                "var_type": var_type,
            }
        )

    return value

def _ger_arg_obj(value):
    if isinstance(value, str) and len(value) > 0:
        pair = re.search(
            r"^\s*(?P<ret_val>([a-zA-Z]+\s+)*([a-zA-Z][\w:]*)\s*(\<.*?\>)?(\s*[&*]{1,2})?)\s+"
            r"(?P<name>[a-zA-Z][\w]*)\s*(?P<list>\[\s*\])?",
            value,
            re.MULTILINE
        )
        if pair != None:
            obj = _get_var_obj(pair.group("ret_val"))
            if not isinstance(obj, Base):
                log.log_error(f"Expected CDataType but got: {obj}")

            value = CVariable(
                pair.group("name"),
                {
                    "datatype": obj,
                    "list": pair.group("list"),
                }
            )

            return value

        else:
            log.log_error(f"Unknown data type: {value}")

    elif isinstance(value, Base):
        return value

    return None

def _update_objs(args, data: dict):
    for file_data in data.values():
        for key, value in file_data.objects.var.items():
            if isinstance(file_data, CFile):
                if isinstance(value, file_data.objects.class_type):
                    value.ret_val.var = _get_var_obj(value.ret_val.var)
                    if not isinstance(value.ret_val.var, Base):
                        log.log_error(f"Expected CDataType but got: {value.ret_val.var}")

                    value.ret_val.var = add_dict(args.data.dtypes, value.ret_val.var)

                    arg_objs = []
                    for arg in value.fnc_args.var:
                        obj = _ger_arg_obj(arg)
                        if obj != None:
                            arg_objs.append(obj)
                            obj.datatype.var = add_dict(args.data.dtypes, obj.datatype.var)
                            obj = add_dict(args.data.vars, obj)

                    value.fnc_args.var = arg_objs

                else:
                    log.log_error(f"Value: {value} not {file_data.objects.class_type}")

                print(key, value)

            else:
                log.log_error(f"Not CFile object: {file_data}")

    return True


def run(args):
    
    _update_objs(args, args.data.files)

    return True