cc_test(
    name = "sample_lib_unit_test",
    copts = ["-Isample"],
    deps = [
        "//sample:sample_lib",
        "@gtest//:gtest_main",

    ],
    srcs = glob(["sample_lib/**/*.cpp"]),
)

