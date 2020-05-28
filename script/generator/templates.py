import general.logger as log

from general.model import *
from templates.globals import TEMPLATES

##############################################################################

def get_cpp_template(fnc_obj: CObject):
    """
    Info: creates a template for GTEST program

    Return: string
    """
    buffer = []

    test_box = TEMPLATES.GTEST["test_box"].format(
        fnc_name = fnc_obj.fnc_name.var,
        fnc_full = fnc_obj.name.var,
    )
    buffer.append(test_box)
    buffer.append('\n')

    return "".join(buffer)

##############################################################################

def get_bazel_template(name: str):
    """
    Info: creates a template for BAZEL script

    Return: string
    """
    buffer = []

    lib_box = TEMPLATES.BAZEL["test_lib"].format(
        lib_name = name + "_unit_test_lib",
        srcs = r'glob("tests/**/*")',
    )
    buffer.append(lib_box)
    buffer.append('\n')

    bin_box = TEMPLATES.BAZEL["test_bin"].format(
        bin_name = name + "_unit_test",
        test_name = name + "_unit_test.cpp",
        lib_name = name + "_unit_test_lib",
    )
    buffer.append(bin_box)
    buffer.append('\n')

    return "".join(buffer)

##############################################################################
