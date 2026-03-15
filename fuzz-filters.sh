#!/bin/bash

AFL_SKIP_CPUFREQ=1 AFL_IGNORE_SEED_PROBLEMS=1 afl-fuzz -i fuzz/input/cli_filters -o fuzz/output/cli_filters -t 10000 -- ./jq -f @@ tests/torture/input0.json

