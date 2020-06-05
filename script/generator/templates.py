import re

from pathlib import Path

import general.logger as log

from general.model import *
from templates.globals import TEMPLATES

##############################################################################
# GTEST TEMPLATES
##############################################################################

def get_cpp_include(args, incl_list: set):
    """
    Info: creates a template of includes for GTEST script

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

def get_cpp_template(args, fnc_obj: CObject, exists: str = "", comment: bool = False):
    """
    Info: creates a template for GTEST item script

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
# PYTEST TEMPLATES
##############################################################################

def get_py_import(args, incl_list: set):
    """
    Info: creates a template of includes for PYTEST script

    Return: string
    """
    buffer = []

    for incl in incl_list:
        buffer.append(TEMPLATES.PYTEST["import_custom"].format(
                incl_path = incl,
            )
        )
    buffer.append('\n')

    return "".join(buffer)

##############################################################################

def get_py_from_import_all(args, incl_list: set):
    """
    Info: creates a template of includes for PYTEST script

    Return: string
    """
    buffer = []

    for incl in incl_list:
        buffer.append(TEMPLATES.PYTEST["from_import_all"].format(
                incl_path = incl,
            )
        )
    buffer.append('\n')

    return "".join(buffer)

##############################################################################

def get_py_template(args, fnc_obj: CObject, exists: str = "", comment: bool = False):
    """
    Info: creates a template for PYTEST item script

    Return: string
    """
    buffer = []
    test_box = ""

    if len(exists) == 0:
        test_box = TEMPLATES.PYTEST["test_box_new"].format(
            fnc_name = fnc_obj.name.var,
            fnc_full = fnc_obj.fnc_name.var,
        )

    else:
        test_box =TEMPLATES.PYTEST["test_box_existing"].format(
            fnc_name = exists,
            fnc_body = fnc_obj.fnc_body.var,
            fnc_full = fnc_obj.fnc_name.var,
        )

    if comment:
        test_box = TEMPLATES.PYTEST["comment"].format(
            comment = test_box,
        )

    buffer.append(test_box)
    buffer.append('\n')

    return "".join(buffer)

##############################################################################

def get_py_class(args, cls_name: str):
    """
    Info: creates a template for main PYTEST script

    Return: string
    """
    buffer = []

    cls_box = TEMPLATES.PYTEST["test_unit"].format(
        cls_file = cls_name[0].upper() + cls_name[1:] + "Test"
    )

    buffer.append(cls_box)
    buffer.append('\n')

    return "".join(buffer)

##############################################################################

def get_py_main(args, includes: set):
    """
    Info: creates a template for main PYTEST script

    Return: string
    """
    buffer = []

    main_box = TEMPLATES.PYTEST["test_main"].format(
        imports = get_py_from_import_all(args, includes)
    )

    buffer.append(main_box)
    buffer.append('\n')

    return "".join(buffer)

##############################################################################
# BAZEL TEMPLATES
##############################################################################

def get_bazel_cpp_template(args, project: Path):
    """
    Info: creates a cpp template for BAZEL script

    Return: string
    """
    buffer = []

    directory =  re.sub(r"(\/\/)|(:.+)", "", project)
    target = project.split(":")[-1].split("//")[-1]

    bin_box = TEMPLATES.BAZEL["cc_test"].format(
        name = target + "_unit_test",
        data = "[]",
        args = "[]",
        copts = TEMPLATES.BAZEL["copts_default"].format(
            project = directory,
        ),
        deps = TEMPLATES.BAZEL["list"].format(
            items = "".join([
                TEMPLATES.BAZEL["item"].format(
                    item = TEMPLATES.BAZEL["label"].format(
                        label = project,
                    ),
                ),
                TEMPLATES.BAZEL["item"].format(
                    item = TEMPLATES.BAZEL["deps_gtest"].format(
                        gtest = args.gtest_name,
                    ),
                ),
            ]),
        ),
        srcs = TEMPLATES.BAZEL["srcs_test_folder"].format(
            test_folder = target,
            types = args.data.ptype,
        ),
    )
    buffer.append(bin_box)
    buffer.append('\n')

    return "".join(buffer)

##############################################################################

def get_bazel_py_template(args, project: Path):
    """
    Info: creates a py template for BAZEL script

    Return: string
    """
    buffer = []

    directory =  re.sub(r"(\/\/)|(:.+)", "", project)
    target = project.split(":")[-1].split("//")[-1]

    bin_box = TEMPLATES.BAZEL["py_test"].format(
        name = target + "_unit_test",
        main = target + "_unit_test.py",
        data = "[]",
        args = "[]",
        deps = TEMPLATES.BAZEL["list"].format(
            items = "".join([
                TEMPLATES.BAZEL["item"].format(
                    item = TEMPLATES.BAZEL["label"].format(
                        label = project,
                    ),
                ),
            ])
        ),
        srcs = TEMPLATES.BAZEL["list"].format(
            items = "".join([
                TEMPLATES.BAZEL["item"].format(
                    item = TEMPLATES.BAZEL["label"].format(
                        label = target + "_unit_test.py",
                    ),
                ),
            ]),
        ) + " + " +
        TEMPLATES.BAZEL["srcs_test_folder"].format(
            test_folder = target,
            types = args.data.ptype,
        ),
    )
    buffer.append(bin_box)
    buffer.append('\n')

    return "".join(buffer)

##############################################################################