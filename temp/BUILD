cc_library(
    name = "sample_unit_test_lib",
    srcs = [
        glob("tests/**/*")
    ],
)

cc_binary(
    name = "sample_unit_test",
    srcs = ["sample_unit_test.cpp"],
    deps = [
        "sample_unit_test_lib"
    ],
)

