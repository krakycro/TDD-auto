import re

from pathlib import Path

import general.logger as log

from general.model import *

##############################################################################

def _get_cpp_var_obj(value):
    if isinstance(value, str):
        if len(value) > 0:
            var_name = re.sub(
                r"\s+(inline)|(constexpr)|(static)\s+",
                "",
                value,
                re.MULTILINE
            )

            is_const = re.search(r"\s*const\s+", var_name, re.MULTILINE)
            var_name = re.sub(r"(\s*const\s+)|( )", "", var_name, re.MULTILINE)
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
                    "var_name": var_name,
                    "var_type": var_type,
                }
            )

        else:
            value = CDataType(
                "",
                {
                    "is_const": False,
                    "var_type": "",
                }
            )

    return value

##############################################################################

def _ger_cpp_arg_obj(value):
    if isinstance(value, str) and len(value) > 0:
        pair = re.search(
            r"^\s*(?P<ret_val>([a-zA-Z_]+\s+)*([a-zA-Z_][\w:]*)\s*(\<.*?\>)?(\s*[&*]{1,2})?)\s+"
            r"(?P<name>[a-zA-Z_][\w]*)\s*(?P<list>\[\s*\])?",
            value,
            re.MULTILINE
        )
        if pair != None:
            obj = _get_cpp_var_obj(pair.group("ret_val"))
            if not isinstance(obj, Base):
                log.log_error(f"Expected CDataType but got: {obj}")

            var_list = pair.group("list")
            if var_list == None:
                var_list = ""

            value = CVariable(
                obj.name.var + ' ' + pair.group("name") + var_list,
                {
                    "datatype": obj,
                    "var_name": pair.group("name") + var_list,
                    "list": var_list,
                }
            )

            return value

        else:
            log.log_error(f"Unknown data type: {value}")

    elif isinstance(value, Base):
        return value

    return None

##############################################################################

def _update_cpp_objs(data: Bundle, file_list: dict):
    for file_data in file_list.values():
        for key, value in file_data.objects.var.items():
            if isinstance(file_data, CFile):
                if isinstance(value, file_data.objects.class_type):
                    value.ret_val.var = _get_cpp_var_obj(value.ret_val.var)
                    if not isinstance(value.ret_val.var, Base):
                        log.log_error(f"Expected CDataType but got: {value.ret_val.var}")

                    value.ret_val.var = add_dict(data.dtypes, value.ret_val.var)

                    arg_objs = []
                    for arg in value.fnc_args.var:
                        obj = _ger_cpp_arg_obj(arg)
                        if obj != None:
                            arg_objs.append(obj)
                            obj.datatype.var = add_dict(data.dtypes, obj.datatype.var)
                            obj = add_dict(data.vars, obj)

                    value.fnc_args.var = arg_objs

                else:
                    log.log_error(f"Value: {value} not {file_data.objects.class_type}")

                # log.log_info(key, value)

            else:
                log.log_error(f"Not CFile object: {file_data}")

    return True

##############################################################################

def run(data: Bundle):

    if data.ptype in log.TYPE_LIST_C:
        _update_cpp_objs(data, data.files_in)

    else:
        log.log_warning(f"Not yet support for linking {data.ptype}!")

    return True

##############################################################################
