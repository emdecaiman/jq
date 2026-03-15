#!/bin/bash

afl-cmin -i fuzz/input/cli_filters -o fuzz/input/asan-ubsan/cli_filters_min -- ./jq-asan-ubsan -f @@ tests/torture/input0.json
afl-cmin -i fuzz/input/cli_json -o fuzz/input/asan-ubsan/cli_json_min -- ./jq-asan-ubsan '.' @@