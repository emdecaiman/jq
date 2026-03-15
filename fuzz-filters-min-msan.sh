#!/bin/bash

AFL_AUTORESUME=1 AFL_SKIP_CPUFREQ=1 AFL_IGNORE_SEED_PROBLEMS=1 afl-fuzz -i fuzz/input/cli_filters_min -o fuzz/output/msan/cli_filters -t 10000 -- ./jq-msan -f @@ tests/torture/input0.json

