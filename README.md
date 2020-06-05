# Test driven development automation tool

## General

This Python script generates test files for each function (or ignores it if already present) from selected project directory.
This tool also generates BUILD file. (C, C++ requires gtest, Python unittest)
Supports C, C++ and Python languages.

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
