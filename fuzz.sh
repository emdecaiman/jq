#!/bin/bash

afl-fuzz -i fuzz-corpus -o output -- ./jq '.' @@

