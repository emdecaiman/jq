#!/bin/bash

AFL_AUTORESUME=1 AFL_SKIP_CPUFREQ=1 AFL_IGNORE_SEED_PROBLEMS=1 AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=0 afl-fuzz -x fuzz/dictionaries/jq_grammar.dict -i fuzz/input/msan/cli_filters_min -o fuzz/output/msan-dict/cli_filters -t 10000 -- ./jq-msan -f @@ fuzz/input/input0.json

