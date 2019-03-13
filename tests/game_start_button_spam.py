# RUN: ./tbin/test_coverage.sh %s %t

from libs.test_utils import TimeoutTest
from host import Lobby, SpacehackFactory

mqtt_factory = SpacehackFactory.mqtt_factory()
l = Lobby(mqtt_factory)

c = mqtt_factory.new()
c.connect()

test = TimeoutTest(30.0)

def start(topic, payload):
    """ Handler for start topic messages """
    # Check that two players are joined
    assert len(payload.split(',')) == 3
    # Test has passed
    test.passed()

def act():
    # Register handler
    c.sub('start', start)
    l.await_init_done()
    # Simulate players joining
    l.wait(0.1)
    c.pub('1/join', '1')
    c.pub('2/join', '1')
    c.pub('3/join', '1')
    l.wait(0.1)
    c.pub('1/join', '1') # Here to make sure things work when you repeatedly send the same value
    c.pub('3/join', '0')
    l.wait(0.1)
    c.pub('1/join', '1')
    c.pub('3/join', '1')
    c.pub('1/join', '1')
    l.wait(0.1)
    c.pub('3/join', '0')
    c.pub('1/join', '1')
    test.await_completion()
    l.stop()

test.run(l.start, act)
