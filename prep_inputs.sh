#!/bin/bash

afl-cmin -i fuzz/input/cli_filters -o fuzz/input/cli_filters_min -- ./jq -f @@ tests/torture/input0.json
afl-cmin -i fuzz/input/cli_json -o fuzz/input/cli_json_min -- ./jq '.' @@