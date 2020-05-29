import general.logger as log

from general.model import *
from templates.globals import TEMPLATES

##############################################################################

def get_cpp_include():
    """
    Info: creates a template for BAZEL script

    Return: string
    """
    buffer = []

    lib_box = TEMPLATES.GTEST["include"]
    buffer.append(lib_box)
    buffer.append('\n')


    return "".join(buffer)

##############################################################################

def get_cpp_template(fnc_obj: CObject, exists:str = ""):
    """
    Info: creates a template for GTEST program

    Return: string
    """
    buffer = []

    if len(exists) == 0:
        test_box = TEMPLATES.GTEST["test_box"].format(
            fnc_name = fnc_obj.name.var,
            fnc_full = fnc_obj.fnc_name.var,
        )
        buffer.append(test_box)
        buffer.append('\n')

    else:
        exist_box = TEMPLATES.GTEST["exist_box"].format(
            fnc_name = exists,
            fnc_body = fnc_obj.fnc_body.var,
        )
        buffer.append(exist_box)
        buffer.append('\n')

    return "".join(buffer)

##############################################################################

def get_bazel_template(name: str):
    """
    Info: creates a template for BAZEL script

    Return: string
    """
    buffer = []

    bin_box = TEMPLATES.BAZEL["test_bin"].format(
        name = name + "_unit_test",
        srcs = r'glob(["tests/**/*"])',
        deps = r'["@gtest//:gtest_main"]',
    )
    buffer.append(bin_box)
    buffer.append('\n')

    return "".join(buffer)

##############################################################################
