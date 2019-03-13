# RUN: ./tbin/test_coverage.sh %s %t
# XFAIL: *

# This test is expected to fail for now, still working on console implementation

from libs.test_utils import TimeoutTest
from host import Lobby, SpacehackFactory

mqtt_factory = SpacehackFactory.mqtt_factory()
l = Lobby(mqtt_factory)

c = mqtt_factory.new()
c.connect()

test = TimeoutTest(10.0)

game_id = None
consoles = None
ready = []

def start(topic, payload):
    """ Handler for start topic messages """
    global game_id, consoles, c
    game_id, *consoles = payload.split(',')
    assert len(consoles) == 2
    c.stop()
    c = mqtt_factory.new(game_id)
    c.connect()
    c.sub('ready', console_ready)
    
def console_ready(topic, payload):
    print(topic, payload)
    _, _, console, _ = topic.split(',')
    global ready
    ready.append(console)
    if set(ready) == set(consoles):
        test.passed()

def act():
    # Register handler
    c.sub('start', start)
    l.await_init_done()
    # Simulate players joining
    l.wait(0.1)
    # TODO
    test.await_completion()
    l.stop()

test.run(l.start, act)
