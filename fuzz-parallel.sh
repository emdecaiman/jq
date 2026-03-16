#!/bin/bash

# You will need to install `screen` to run multiple fuzzers in parallel. 
# You can attach to the screen session with `screen -r fuzzer01_asan_ubsan` and detach with `Ctrl-A D`. You can also use `screen -ls` to list all screen sessions and `screen -r <session_name>` to attach to a specific session.
# 
# To install `screen` on Ubuntu, you can use the following command:
# `sudo apt update && sudo apt install screen`
# 
# To check the status of the fuzzing campaign, run:
# `afl-whatsup -s fuzz/output/sync`

MEMORY_LIMIT=$((1048576 * 300)) # 300 MiB, to avoid OOM kills on the fuzzers 
DICT="fuzz/dictionaries/jq_grammar.dict"


AFL_TESTCACHE_SIZE=$((1048576 * 500)) # 500 MiB
AFL_AUTORESUME=1
AFL_SKIP_CPUFREQ=1
AFL_IGNORE_SEED_PROBLEMS=1
AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=0
AFL_LLVM_LAF_ALL=1
AFL_FINAL_SYNC=1
# AFL_IMPORT_FIRST=1

mkdir -p fuzz/output/sync

screen -dmS "asan_ubsan" afl-fuzz -M "asan_ubsan" -i fuzz/input/cli_filters_min -o fuzz/output/sync -t 10000 -m $MEMORY_LIMIT -- ./jq-asan-ubsan -f @@ fuzz/input/input0.json
screen -dmS "asan_ubsan_dict" afl-fuzz -S "asan_ubsan_dict" -x $DICT -i fuzz/input/cli_filters_min -o fuzz/output/sync -t 10000 -m $MEMORY_LIMIT -- ./jq-asan-ubsan -f @@ fuzz/input/input0.json
screen -dmS "asan_ubsan_dict_fast" afl-fuzz -S "asan_ubsan_dict_fast" -x $DICT -i fuzz/input/cli_filters_min -o fuzz/output/sync -p fast -t 10000 -m $MEMORY_LIMIT -- ./jq-asan-ubsan -f @@ fuzz/input/input0.json
screen -dmS "asan_ubsan_dict_exploit" afl-fuzz -S "asan_ubsan_dict_exploit" -x $DICT -i fuzz/input/cli_filters_min -o fuzz/output/sync -p exploit -t 10000 -m $MEMORY_LIMIT -- ./jq-asan-ubsan -f @@ fuzz/input/input0.json
# screen -dmS "asan_ubsan_dict_mmopt" afl-fuzz -S "asan_ubsan_dict_mmopt" -x $DICT -i fuzz/input/cli_filters_min -o fuzz/output/sync -L 0 -p mmopt -t 10000 -m $MEMORY_LIMIT -- ./jq-asan-ubsan -f @@ fuzz/input/input0.json

screen -dmS "msan" afl-fuzz -S "msan" -i fuzz/input/cli_filters_min -o fuzz/output/sync -t 10000 -m $MEMORY_LIMIT -- ./jq-msan -f @@ fuzz/input/input0.json
screen -dmS "msan_dict" afl-fuzz -S "msan_dict" -x $DICT -i fuzz/input/cli_filters_min -o fuzz/output/sync -t 10000 -m $MEMORY_LIMIT -- ./jq-msan -f @@ fuzz/input/input0.json
# screen -dmS "msan_dict_fast" afl-fuzz -S "msan_dict_fast" -x $DICT -i fuzz/input/cli_filters_min -o fuzz/output/sync -p fast -t 10000 -m $MEMORY_LIMIT -- ./jq-msan -f @@ fuzz/input/input0.json
# screen -dmS "msan_dict_exploit" afl-fuzz -S "msan_dict_exploit" -x $DICT -i fuzz/input/cli_filters_min -o fuzz/output/sync -p exploit -t 10000 -m $MEMORY_LIMIT -- ./jq-msan -f @@ fuzz/input/input0.json
# screen -dmS "msan_dict_mmopt" afl-fuzz -S "msan_dict_mmopt" -x $DICT -i fuzz/input/cli_filters_min -o fuzz/output/sync -L 0 -p mmopt -t 10000 -m $MEMORY_LIMIT -- ./jq-msan -f @@ fuzz/input/input0.json

