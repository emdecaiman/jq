#!/bin/bash
git submodule update --init && autoreconf -i && export AFL_USE_ASAN=1 && CC=afl-clang-fast CXX=afl-clang-fast++ ./configure --with-oniguruma=builtin --enable-all-static && make clean && make -j8
