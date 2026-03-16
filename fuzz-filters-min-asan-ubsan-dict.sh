#!/bin/bash

AFL_AUTORESUME=1 AFL_SKIP_CPUFREQ=1 AFL_IGNORE_SEED_PROBLEMS=1 AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=0 AFL_LLVM_CMPLOG=1 AFL_LLVM_LAF_ALL=1 afl-fuzz -x fuzz/dictionaries/jq_grammar.dict -i fuzz/input/asan-ubsan/cli_filters_min -o fuzz/output/asan-ubsan-dict/cli_filters -t 10000 -- ./jq-asan-ubsan -f @@ fuzz/input/input0.json

