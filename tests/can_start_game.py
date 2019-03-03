# RUN: python %s

from libs.test_utils import TimeoutTest
from host import Lobby, MqttWrapper

l = Lobby(MqttWrapper())
service = l.get_service()

c = MqttWrapper()
c.connect()

test = TimeoutTest(10.0)

def start(topic, payload):
    """ Handler for start topic messages """
    # Check that two players are joined
    assert len(payload.split(',')) == 2
    # Test has passed
    test.passed()

def act():
    # Register handler
    c.sub('spacehack/start', start)
    # Simulate players joining
    service.wait(0.1)
    c.pub('spacehack/1/join', '1')
    c.pub('spacehack/2/join', '1')

def run_unit():
    service.start()
    service.wait(6.0)
    service.stop()

test.run(run_unit, act)
