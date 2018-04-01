#!/bin/sh -ex

make travis CC=clang
make travis CC=gcc
make travis CC=i686-w64-mingw32-gcc HOST="--host=i686-w64-mingw32" TEST="unittest/run.exe"
make travis CC=clang CFLAGS="-fsanitize=undefined" ASAN_OPTIONS="detect_leaks=0"
make travis CC=clang CFLAGS="-fsanitize=address -g" ASAN_OPTIONS="detect_leaks=0"
make travis CC=clang TEST=analyze