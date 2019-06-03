# RUN: ./tbin/test_coverage.sh %s %t
# XFAIL: *

# This test is expected to fail for now, still working on console implementation

from libs.test_utils import TimeoutTest
from host import Lobby, HostFactory
from console import ConsoleFactory
from mock_hardware import MockButton
import config
from services import Service

conf = config.build()

mqtt_factory = HostFactory.mqtt_factory(conf)

# Create a lobby, some join buttons, and some joiners
l = Lobby(conf, mqtt_factory)
join_buttons = [MockButton({}) for i in range(2)]
console_joiners = [ConsoleFactory.joiner(conf, join_buttons[i], "console_%d" % (i)) for i in range(2)]

# connect test's mqtt listener
m = mqtt_factory.new()
m.connect()

test = TimeoutTest(10.0)

start_game_id = None
start_consoles = []
ready_game_ids = []
ready_consoles = []

# The consoles send ready messages and the host sends a game start message.
# We need to check that these messages are all consistent.
# This is done in this test a way that enable the messages to be processed
# in any order. As long as the messages match.
# check_pass_condition() checks if they match

def check_pass_condition():
    global start_game_id, start_consoles, ready_game_ids, ready_consoles
    if (sorted(ready_consoles) == sorted(start_consoles) and
            all(gid == start_game_id for gid in ready_game_ids)):
        test.passed()

def start(topic, payload):
    """ Handler for start topic messages """
    global start_game_id, start_consoles
    start_game_id, *start_consoles = payload.split(',')
    assert len(start_consoles) == 2
    check_pass_condition()
    
def console_ready(topic, payload):
    """ Handler for ready topic messages """
    global ready_game_ids, ready_consoles
    _, game_id, console, _ = topic
    ready_game_ids.append(game_id)
    ready_consoles.append(console)
    check_pass_condition()

def startup():
    # Start the loby
    l.start()
    # Start the console joiners
    for joiner in console_joiners:
        joiner.start()

def mqtt_message(topic, payload):
    if len(topic) >= 4:
        root, game, console, subtopic, *tail = topic
        if subtopic == 'ready' and tail == []:
            console_ready(topic, payload)

def act():
    # Register handler
    m.sub('start', start)
    m.sub('#', mqtt_message)
    l.await_init_done()
    for joiner in console_joiners:
        joiner.await_init_done()
    # Simulate players joining
    for button in join_buttons:
        button.press()
    l.wait(6.0)
    for button in join_buttons:
        button.release()
    test.await_completion()
    Service.stop_all()

test.run(startup, act)
