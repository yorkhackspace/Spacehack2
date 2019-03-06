[![Build Status](https://travis-ci.org/yorkhackspace/Spacehack2Host.svg?branch=master)](https://travis-ci.org/yorkhackspace/Spacehack2Host)
[![Coverage Status](https://coveralls.io/repos/github/yorkhackspace/Spacehack2Host/badge.svg?branch=master)](https://coveralls.io/github/yorkhackspace/Spacehack2Host?branch=master)

# Spacehack 2

This is a rewrite of the code that runs spacehack.

This repository contains the host side of the system (the part that 'runs the game').

Consoles connect to the host to join a game.

## Running and developing

### Prerequisites:

(Installation instructions below)

- python3.6 (or later. Older pythons are probably fine too, maybe)
- python3 development sources (required by lit to do timeout tests for some reason)
- mosquitto (or any other standard mqtt broker)
- various python packages (see requirements.txt)

#### Ubuntu packages:
`apt install python3 python3-dev mosquitto`

#### Python packages:

We recommend installing these in a venv, there is a script that does this for you:

`./init_venv.sh`

Then you can source the venv in your shell:

`source venv/bin/activate` or similar for your shell

If you really want to you could instead install manually with `pip install -r requirements.txt`

#### Running stuff

First make sure your mqtt broker is running.

You can then check if everything worked with:

`./tests.sh`

And you can run the host in the same way:

`./host.py`
