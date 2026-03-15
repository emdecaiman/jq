#!/bin/bash

AFL_SKIP_CPUFREQ=1 AFL_IGNORE_SEED_PROBLEMS=1  afl-fuzz -i fuzz/input/cli_json -o fuzz/output/cli_json  -t 10000  -- ./jq '.' @@

