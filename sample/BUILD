_COPTS = [
    "/std:c++17", # "-std=c++17",
    "-Isample",
]

cc_library(
    name = "sample_lib",
    srcs = [
        "sample_run.cpp"
    ] + glob(["srcs/**/*"]),
    hdrs = glob(["hdrs/**/*"]),
    copts = _COPTS,
)

cc_binary(
    name = "sample",
    srcs = ["sample_main.cpp"],
    copts = _COPTS,
    deps = ["sample_lib"],
)