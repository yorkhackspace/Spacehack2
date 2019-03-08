# Test bin directory

This directory contains all the scripts required for running and debugging the test suite (in theory).

It is intended that this directory is safe to have on your path.

`run_all_spacehack_tests` - Runs all of the tests, this is what the travis build will run

`run_with_python_path` - Run a program with the current directory on the python path (useful for running tests without the LIT framework around it)

`debug_spacehack_test` - debugs a test (just runs lit with --verbose and the test you run)

