#!/bin/bash

AFL_AUTORESUME=1 AFL_SKIP_CPUFREQ=1 AFL_IGNORE_SEED_PROBLEMS=1 afl-fuzz -i fuzz/input/asan-ubsan/cli_filters_min -o fuzz/output/asan-ubsan/cli_filters -t 10000 -- ./jq-asan-ubsan -f @@ tests/torture/input0.json

