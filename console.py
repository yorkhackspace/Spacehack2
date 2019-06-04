#!/usr/bin/env python
import signal
from mqtt_wrapper import MqttWrapperFactory
from services import Service
import config
import random

class ConsoleFactory:
    def mqtt_factory(config):
        return MqttWrapperFactory(topic_prefix=config['root_topic']+'/')

    def joiner(config, join_control, console_id):
        return Joiner(ConsoleFactory.mqtt_factory(config), config, join_control, console_id)

    def game_client(config, game_id, console_id):
        return GameClient(ConsoleFactory.mqtt_factory(config), game_id, console_id)

class GameClient(Service):
    def __init__(self, mqtt_factory, game_id, console_id):
        super(GameClient, self).__init__()
        self.gid = game_id
        self.cid = console_id
        self.mqtt = mqtt_factory.new('/'.join([self.gid, self.cid]))

    def init(self):
        self.mqtt.connect()
        self.mqtt.pub('ready', 'ready')

    def run(self):
        pass

    def cleanup(self):
        self.mqtt.stop()

class Joiner(Service):
    def __init__(self, mqtt_factory, config, join_control, console_id):
        super(Joiner, self).__init__()
        self.config = config
        self.gid = None
        self.cid = console_id
        self.mqtt = mqtt_factory.new(self.cid)
        self.join_mqtt = mqtt_factory.new()
        self.button = join_control

    def start_game(self, topic, payload):
        game_id, *joined_consoles = [s.strip() for s in payload.split(',')]
        if self.cid in joined_consoles:
            self.gid = game_id
            self.start_subservice(ConsoleFactory.game_client(self.config, game_id, self.cid))

    def init(self):
        self.mqtt.connect()
        self.join_mqtt.connect()
        self.join_mqtt.sub('start', self.start_game)
        self.button.set_callback(self.button_changed)
        self.button.connect()

    def button_changed(self, newstate):
        if newstate in [0,1]:
            self.mqtt.pub('/join', str(newstate))
        else:
            print("Warning: Unknown button state: %r" % (newstate))

    def run(self):
        # This service doesn't need to do anything in the main run function
        # Just wait until the service is told to stop
        self.stopped.wait()

    def cleanup(self):
        self.mqtt.stop()
        self.join_mqtt.stop()

class SpacehackConsole:
    def __init__(self, config, mqtt_factory=None):
        self.mqtt_factory=mqtt_factory
        if self.mqtt_factory is None:
            self.mqtt_factory = ConsoleFactory.mqtt_factory(config)
        self.conf = config
        self.cid = str(self.conf['id'])
        
        # TODO don't use None for the button, load details from config
        self.joiner = Joiner(self.mqtt_factory, None, self.cid)

    def stop(self):
        Service.stop_all()
        Service.wait_all()

    def start(self):
        self.joiner.start()

    def wait(self):
        Service.wait_all()

if __name__ == '__main__':
    config = config.load('console_config.toml')
    sh = SpacehackConsole(config)
    def signal_handler(sig, frame):
        print('Exit')
        sh.stop()
        sh.wait()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    sh.start()
    sh.wait()

class ControlPanel:
    def __init__(self):
        self.clear()

    def clear(self):
        self.components = []
        self.busy_components = []

    def add_component(self, component):
        self.components.append(component)

    def free_components(self):
        busy = self.busy_components
        return [c for c in self.components if c not in busy]

    def get_component(self):
        c = random.choice(self.free_components())
        self.busy_components.append(component)

    def release_component(self, component):
        self.busy_components.remove(component)

    def poll(self):
        for c in self.components:
            c.poll()
