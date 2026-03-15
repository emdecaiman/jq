#!/bin/bash


autoreconf -fi 
export AFL_USE_ASAN=1
export AFL_USE_UBSAN=1
CC=afl-clang-fast CXX=afl-clang-fast++  CFLAGS="-fsanitize=fuzzer,address,undefined" LDFLAGS="-fsanitize=fuzzer,address,undefined" ./configure --with-oniguruma=builtin --enable-all-static --disable-shared


make clean
make -j8

# Compile the fuzzing harness
afl-clang-fast "-fsanitize=fuzzer,address,undefined" fuzz_jq_persistent.c -I./src -I./src/jv -I./libjq.la -I./libjv.la -o fuzz_jq_persistent

