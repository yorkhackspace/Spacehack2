#!/usr/bin/env python
from mqtt_wrapper import MqttWrapperFactory
import signal
import sys
from GameStarter import GameStarter
import time
from functools import wraps
from threading import Event, Thread
import os
from services import Service

class SpacehackConfiguration:
    GAME_START_DELAY = 5.0
    JOIN_GAME_DELAY = 1.0
    LEAVE_GAME_DELAY = 0.5

    def root_topic():
        env_topic = os.environ.get('SH_TOPIC_PREFIX_OVERRIDE') or 'spacehack'
        return ''.join(c if c not in '\/.#$+_' else '-' for c in env_topic) + '/'

class SpacehackFactory:
    def mqtt_factory():
        return MqttWrapperFactory(topic_prefix=SpacehackConfiguration.root_topic())

    def game_starter():
        sc = SpacehackConfiguration
        return GameStarter(sc.GAME_START_DELAY, sc.JOIN_GAME_DELAY, sc.LEAVE_GAME_DELAY)

    def game_runner(game_subtopic, consoles):
        return GameRunner(SpacehackFactory.mqtt_factory(), game_subtopic, consoles)

class Lobby(Service):
    def __init__(self, mqtt_factory):
        super(Lobby, self).__init__()
        self.mqtt = mqtt_factory.new()
        self.next_game_id = 0

    def get_next_game_id(self):
        this_id = "game_%d" % (self.next_game_id)
        self.next_game_id += 1
        return this_id

    def handle_join(self, topic, payload):
        _, console, *_ = topic.split('/')
        player = self.gamestarter.player(console)
        print('Payload "%s" on "%s"' %(payload, topic))
        if payload == '1':
            player.push()
        elif payload == '0':
            player.release()
        else:
            print('Unknown payload "%s" on "%s"' %(payload, topic))

    def init(self):
        self.mqtt.connect()
        self.gamestarter = SpacehackFactory.game_starter()
        self.mqtt.sub('+/join', self.handle_join)

    def run(self):
        while(not self.stopped.isSet()):
            self.sleep(0.05)
            self.gamestarter.step_time(0.05)
            if(self.gamestarter.should_start):
                game_id = self.get_next_game_id() 
                SpacehackFactory.game_runner(game_id, self.gamestarter.joined_players)
                self.mqtt.pub('start', ','.join([game_id, *self.gamestarter.joined_players]))
                self.gamestarter.reset()

    def cleanup(self):
        self.mqtt.stop()

class GameRunner(Service):
    def __init__(self, mqtt_factory, game_subtopic, consoles):
        super(GameRunner, self).__init__()
        self.mqtt_factory = mqtt_factory
        self.game_subtopic = game_subtopic
        self.mqtt = mqtt_factory.new(game_subtopic)
        self.consoles = consoles
        self.ready_consoles = []
        self.all_ready = Event()
        self.game_func = None
        self.next_round = 0

    def get_next_round_id(self):
        round_id = 'round_%d' % (self.next_round)
        self.next_round += 1
        return round_id

    def intertupt(self):
        self.all_ready.set()

    def handle_console_ready(self, topic, payload):
        print("Topic: %s" % (topic))
        _, _, console, _ = topic.split('/')
        if payload != 'ready':
            return
        if console not in self.read_consoles:
            self.ready_consoles.append(console)
        if all(c in ready_consoles for c in self.consoles):
            self.all_ready.set()

    def init(self):
        self.mqtt.connect()
        self.mqtt.sub('+/ready', self.handle_console_ready)

    def start_next_round(self):
        # Replace mqtt instance with new one for this round
        self.mqtt.stop()
        self.mqtt = self.mqtt_factory.new('/'.join(self.game_subtopic, self.get_next_round_id()))
        self.mqtt.connect()
        # TODO sub to round-specific topics
        #self.mqtt.sub(thingy, handle_thingy)
        self.game_func = self.game_round

    def game_splash(self):
        self.mqtt.pub('splash/text', '***** SPACEHACK *****')
        self.sleep(4.0)
        self.mqtt.pub('splash/text', 'Wheeeeeeeeeeeeee')
        self.sleep(10.0)
        self.start_next_round()

    def game_round(self):
        # TODO
        self.sleep(10)

    def run(self):
        self.all_ready.wait()
        self.game_func = self.game_splash
        while not self.stopped.is_set():
            self.game_func()

    def cleanup(self):
        self.mqtt.stop()

class SpacehackHost:
    def __init__(self, mqtt_factory=SpacehackFactory.mqtt_factory()):
        self.mqtt_factory=mqtt_factory
        self.lobby = Lobby(self.mqtt_factory)

    def stop(self):
        Service.stop_all()
        Service.wait_all()

    def start(self):
        self.lobby.start()

    def wait(self):
        Service.wait_all()


if __name__ == '__main__':
    sh = SpacehackHost()
    def signal_handler(sig, frame):
        print('Exit')
        sh.stop()
        sh.wait()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    sh.start()
    sh.wait()
