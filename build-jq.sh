#!/bin/bash

set -e

git submodule update --init 
autoreconf -fi 
export AFL_USE_ASAN=1
CC=afl-clang-fast CXX=afl-clang-fast++ ./configure --with-oniguruma=builtin --enable-all-static --disable-shared
make clean
make -j8
