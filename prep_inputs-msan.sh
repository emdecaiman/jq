#!/bin/bash

afl-cmin -i fuzz/input/cli_filters -o fuzz/input/msan/cli_filters_min -- ./jq-msan -f @@ tests/torture/input0.json
afl-cmin -i fuzz/input/cli_json -o fuzz/input/msan/cli_json_min -- ./jq-msan '.' @@