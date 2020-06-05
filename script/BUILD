package(default_visibility = ["//visibility:public"])

py_library(
    name = "script_lib",
    srcs = glob(["**/*.py"]),
)

py_binary(
    name = "script",
    srcs = ["script.py"],
    deps = ["script_lib"],
)
