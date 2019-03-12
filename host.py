#!/usr/bin/env python
from paho.mqtt import client as mqtt
from mqtt_wrapper import MqttWrapper
import signal
import sys
from GameStarter import GameStarter
import time
from functools import wraps
from threading import Event, Thread

class LobbyConfiguration:
    GAME_START_DELAY = 5.0
    JOIN_GAME_DELAY = 1.0
    LEAVE_GAME_DELAY = 0.5


class Service:
    def __init__(self):
        self.stopped = Event()
        self.init_done = Event()

    def stop(self):
        self.stopped.set()

    def await_init_done(self):
        self.init_done.wait()

    def wait(self, *args):
        self.svc_thread.join(*args)

    def init(self):
        # Some services might not need to do setup, so it's OK not to override
        pass

    def run(self):
        raise Exception("Service.run(): Implement this in subclass")

    def service_thread(self):
        self.init()
        self.init_done.set()
        self.run()

    def start(self, synchronous_init=False):
        self.svc_thread = Thread(target=self.service_thread)
        self.svc_thread.start()
        if synchronous_init:
            self.await_init_done()

class Lobby(Service):
    def __init__(self, mqtt):
        super(Lobby, self).__init__()
        self.mqtt = mqtt

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
        lc = LobbyConfiguration
        self.gamestarter = GameStarter(lc.GAME_START_DELAY, lc.JOIN_GAME_DELAY, lc.LEAVE_GAME_DELAY)
        self.mqtt.sub('+/join', self.handle_join)

    def run(self):
        while(not self.stopped.isSet()):
            self.stopped.wait(0.05)
            self.gamestarter.step_time(0.05)
            if(self.gamestarter.should_start):
                self.mqtt.pub('start', ','.join(self.gamestarter.joined_players))
                self.gamestarter.reset()

class SpacehackHost:
    def __init__(self, mqtt=MqttWrapper()):
        self.mqtt = mqtt
        self.lobby = Lobby(mqtt)

    def stop(self):
        self.lobby.stop()
        self.mqtt.stop()
        self.lobby.wait(10.0)

    def start(self):
        self.lobby.start()

    def wait(self):
        self.lobby.wait()


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
