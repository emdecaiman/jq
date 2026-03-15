#!/bin/bash

set -e

git submodule update --init 
autoreconf -fi 
export AFL_HARDEN=1
ENABLE_ALL_STATIC=1 CC=afl-clang-fast CXX=afl-clang-fast++ ./configure --with-oniguruma=builtin --enable-all-static --disable-shared
make clean
make -j8
