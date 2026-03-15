#!/bin/bash

AFL_AUTORESUME=1 AFL_SKIP_CPUFREQ=1 AFL_IGNORE_SEED_PROBLEMS=1 AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=0 afl-fuzz -i fuzz/input/asan-ubsan/cli_filters_min -o fuzz/output/asan-ubsan/cli_filters -t 10000 -- ./jq-asan-ubsan -f @@ fuzz/input/input0.json

