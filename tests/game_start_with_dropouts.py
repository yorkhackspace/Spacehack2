# RUN: ./tbin/test_coverage.sh %s %t

from libs.test_utils import TimeoutTest
from host import Lobby, MqttWrapper

l = Lobby(MqttWrapper())
service = l.get_service()

c = MqttWrapper()
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
    service.await_init_done()
    # Simulate players joining
    service.wait(0.1)
    c.pub('1/join', '1')
    c.pub('2/join', '1')
    c.pub('3/join', '1')
    service.wait(0.5)
    c.pub('2/join', '0')
    c.pub('3/join', '0')
    service.wait(10.0)
    c.pub('2/join', '1')
    service.wait(1.0)
    c.pub('3/join', '1')
    test.await_completion()
    service.stop()

def run_unit():
    service.start()
    service.wait(20.0)
    service.stop()

test.run(run_unit, act)
