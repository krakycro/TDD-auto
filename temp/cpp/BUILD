cc_test(
    name = "sample_lib_unit_test",
    data = [],
    args = [],
    srcs = glob(["sample_lib/**/*.cpp"]),
    copts = ["-Isample"],
    deps = [
        "//sample:sample_lib",
        "@gtest//:gtest_main",
    ],
)

