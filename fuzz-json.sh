#!/bin/bash

AFL_IGNORE_SEED_PROBLEMS=1  afl-fuzz -i fuzz/input/cli_json -o fuzz/output/cli_json -- ./jq '.' @@

