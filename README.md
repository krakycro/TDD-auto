# Test driven development automation tool

### This is an alpha version! 

Version: 0.1.0

## General

This Python script generates test files for each function (or ignores it if already present) from selected project directory.
This tool also generates BUILD file for Bazel support. (C, C++ requires googletest and Python requires unittest)

Supports C, C++ and Python languages.

## Requirements

This Python script parsing capabilities are bit restricted, so clean code is recommended. (LLVM, PEP8)
But majority boils down to:

* For C, C++ additionaly after placiong ';', at the end of class or struct, also place the comment: "// class|struct {name}",
  * Also do this for namespaces after the end: "// namespace {name}",
* For Python make sure that empty lines do not contain any spaces, nor do use tabs as whitespaces.

## Arguments:

* -h, --help
  * Show this help message and exit
* -i INPUT_FOLDER, --input_folder INPUT_FOLDER
  * Input data. Mandatory field.
* -o OUTPUT_FOLDER, --output_folder OUTPUT_FOLDER
  * Output data. Optional field.
* -it INPUT_TYPE, --input_type INPUT_TYPE
  * Text type. Default: auto
* --data DATA
  * Existing data to load. Default: None
* --target_label TARGET_LABEL
  * Absolute label path of project. Default: None
* --gtest_name GTEST_NAME
  * Name of gtest workspace. Default: gtest
* --ignore_info
  * Ignore info log messages.
* --ignore_warning
  * Ignore warning log messages.
* --ignore_error
  * Ignore error log messages.
