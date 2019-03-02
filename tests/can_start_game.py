# RUN: python %s

from libs.test_utils import TimeoutTest
from host import SpacehackHost, MqttWrapper

sh = SpacehackHost()
sh.main()

c = MqttWrapper()
c.connect()

test = TimeoutTest()

def start(topic, payload):
    """ Handler for start topic messages """
    # Check that two players are joined
    assert payload == '2'
    # Test has passed
    test.passed()

def act():
    # Register handler
    c.sub('spacehack/start', start)
    # Simulate players joining
    c.pub('spacehack/1/join', '1')
    c.pub('spacehack/2/join', '1')

test.run(sh.gamestart_loop, act)
