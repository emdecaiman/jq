#!/bin/bash

afl-fuzz -i fuzz-corpus -o fuzz-output -- ./jq '.' @@

