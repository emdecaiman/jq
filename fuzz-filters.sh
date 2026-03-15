#!/bin/bash

AFL_IGNORE_SEED_PROBLEMS=1 afl-fuzz -i fuzz/input/cli_filters -o fuzz/output/cli_filters -- ./jq -f @@ tests/torture/input0.json

