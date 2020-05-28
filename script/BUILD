py_library(
    name = "script_lib",
    srcs = glob([
        "adapter/*",
        "general/*",
        "generator/*",
    ]),
)

py_binary(
    name = "script",
    srcs = ["script.py"],
    deps = ["script_lib"],
)