import re

from pathlib import Path

import general.logger as log

from general.model import *
from templates.globals import TEMPLATES

##############################################################################
# GTEST TEMPLATES
##############################################################################

def get_cpp_include(incl_list: set):
    """
    Info: creates a template for BAZEL script

    Return: string
    """
    buffer = []

    for incl in incl_list:
        buffer.append(TEMPLATES.GTEST["include_custom"].format(
                incl_path = incl,
            )
        )
    buffer.append('\n')

    buffer.append(TEMPLATES.GTEST["include_gtest"])
    buffer.append('\n')


    return "".join(buffer)

##############################################################################

def get_cpp_template(fnc_obj: CObject, exists: str = "", comment: bool = False):
    """
    Info: creates a template for GTEST program

    Return: string
    """
    buffer = []
    test_box = ""

    if len(exists) == 0:
        test_box = TEMPLATES.GTEST["test_box_new"].format(
            fnc_name = fnc_obj.name.var,
            fnc_full = fnc_obj.fnc_name.var,
        )

    else:
        test_box =TEMPLATES.GTEST["test_box_existing"].format(
            fnc_name = exists,
            fnc_body = fnc_obj.fnc_body.var,
        )

    if comment:
        test_box = TEMPLATES.GTEST["comment"].format(
            comment = test_box,
        )

    buffer.append(test_box)
    buffer.append('\n')

    return "".join(buffer)

##############################################################################
# BAZEL TEMPLATES
##############################################################################

def get_bazel_template(project: Path):
    """
    Info: creates a template for BAZEL script

    Return: string
    """
    buffer = []

    directory =  re.sub(r"(\/\/)|(:.+)", "", project)
    target = project.split(":")[-1]

    bin_box = TEMPLATES.BAZEL["test_bin"].format(
        name = target + "_unit_test",
        copts = TEMPLATES.BAZEL["copts_default"].format(
            project = directory,
        ),
        deps = TEMPLATES.BAZEL["list"].format(
            items = "".join([
                TEMPLATES.BAZEL["item"].format(
                    item = TEMPLATES.BAZEL["label"].format(
                        label = project,
                    )
                ),
                TEMPLATES.BAZEL["item"].format(
                    item = TEMPLATES.BAZEL["deps_gtest"]
                )
            ])
        ),
        srcs = TEMPLATES.BAZEL["srcs_test_folder"].format(
            test_folder = target,
        ),
    )
    buffer.append(bin_box)
    buffer.append('\n')

    return "".join(buffer)

##############################################################################
