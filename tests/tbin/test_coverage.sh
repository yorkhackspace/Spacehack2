#!/usr/bin/env bash
if [ $# -ne 2 ]; then
    echo "Incorrect invocation of test_coverage.sh script, please check run line"
    echo "(You need to use '%s %t' as the arguments)"
    exit 1
fi
export SH_TOPIC_PREFIX_OVERRIDE=$2
coverage run --branch --append --source=host,mqtt_wrapper $1
