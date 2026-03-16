#!/bin/bash

MEMORY_LIMIT=$((1048576 * 500)) # 500 MiB, to avoid OOM kills on the fuzzers 
AFL_TESTCACHE_SIZE=$((1048576 * 500)) # 500 MiB
AFL_AUTORESUME=1
AFL_SKIP_CPUFREQ=1
AFL_IGNORE_SEED_PROBLEMS=1
AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=0
AFL_LLVM_LAF_ALL=1
AFL_FINAL_SYNC=1
AFL_IMPORT_FIRST=1
screen -dmS "fuzzer01_asan_ubsan" afl-fuzz -M "fuzzer01_asan_ubsan" -i fuzz/input/cli_filters_min -o fuzz/output/sync -t 10000 -m $MEMORY_LIMIT -- ./jq-asan-ubsan -f @@ fuzz/input/input0.json
screen -dmS "fuzzer02_asan_ubsan_dict" afl-fuzz -S "fuzzer02_asan_ubsan_dict" -x fuzz/dictionaries/jq_grammar.dict -i fuzz/input/cli_filters_min -o fuzz/output/sync -t 10000 -m $MEMORY_LIMIT -- ./jq-asan-ubsan -f @@ fuzz/input/input0.json
screen -dmS "fuzzer03_msan" afl-fuzz -S "fuzzer03_msan" -x fuzz/dictionaries/jq_grammar.dict -i fuzz/input/cli_filters_min -o fuzz/output/sync -t 10000 -m $MEMORY_LIMIT -- ./jq-msan -f @@ fuzz/input/input0.json
screen -dmS "fuzzer04_msan_dict" afl-fuzz -S "fuzzer04_msan_dict" -x fuzz/dictionaries/jq_grammar.dict -i fuzz/input/cli_filters_min -o fuzz/output/sync -t 10000 -m $MEMORY_LIMIT -- ./jq-msan -f @@ fuzz/input/input0.json
screen -dmS "fuzzer05_asan_ubsan_mopt" afl-fuzz -S "fuzzer05_asan_ubsan_mopt" -i fuzz/input/cli_filters_min -o fuzz/output/sync -L 0 -t 10000 -m $MEMORY_LIMIT -- ./jq-msan -f @@ fuzz/input/input0.json
screen -dmS "fuzzer06_asan_ubsan_exploit" afl-fuzz -S "fuzzer06_asan_ubsan_exploit" -i fuzz/input/cli_filters_min -o fuzz/output/sync -p exploit -t 10000 -m $MEMORY_LIMIT -- ./jq-msan -f @@ fuzz/input/input0.json

