#!/usr/bin/env bash
rm -f tests/.coverage # Clear previous coverage report
lit -j1 $@ tests/
cp tests/.coverage .coverage
