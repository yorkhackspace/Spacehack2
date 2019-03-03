#!/usr/bin/env python
from paho.mqtt import client as mqtt
import signal
import sys
from GameStarter import GameStarter
import time
from functools import wraps

class LobbyConfiguration:
    GAME_START_DELAY = 5.0
    JOIN_GAME_DELAY = 1.0
    LEAVE_GAME_DELAY = 0.5

class MqttWrapper:
    def __init__(self, address='localhost', port=1883):
        self.address = address
        self.port = port

    def on_connect(self, client, userdata, flags, rc):
        print("connected to mqtt")

    def connect(self):
        self.mqtt = mqtt.Client()
        self.mqtt.on_connect = self.on_connect
        self.mqtt.connect(self.address, self.port, 60)
        self.mqtt.loop_start()

    def stop(self):
        self.mqtt.loop_stop()
        self.mqtt.disconnect()

    def sub(self, topic, callback):
        self.mqtt.subscribe(topic)
        wrapped_callback = self.wrap_message_handler(callback)
        self.mqtt.message_callback_add(topic, wrapped_callback)

    def wrap_message_handler(self, callback):
        @wraps(callback)
        def message_handler_wrapper(client, userdata, message):
            return callback(message.topic, message.payload.decode('utf-8'))
        return message_handler_wrapper

    def pub(self, topic, payload):
        self.mqtt.publish(topic, payload)

    def dump(self, topic, payload):
        print("%s: %s" % (topic, payload))

class SpacehackHost:

    def __init__(self, mqtt=MqttWrapper()):
        self.mqtt = mqtt

    def test_topic(self, client, userdata, message):
        print(message)

    def handle_lobby_join(self, topic, payload):
        _, console, *_ = topic.split('/')
        print("Player %s: %s" % (console, payload))
        if payload == '1':
            self.g.player(console).push()
        elif payload == '0':
            self.g.player(console).release()

    def main(self):
        self.mqtt.connect()
        self.mqtt.sub('test', self.test_topic)
        lc = LobbyConfiguration
        self.g = GameStarter(lc.GAME_START_DELAY, lc.JOIN_GAME_DELAY, lc.LEAVE_GAME_DELAY)
        self.mqtt.sub('spacehack/+/join', self.handle_lobby_join)

    def gamestart_loop(self):
        while(not self.g.should_start):
            time.sleep(0.5)
            self.g.step_time(0.5)
        self.mqtt.pub('spacehack/start', ','.join(self.g.joined_players))
        print("Total startable players: %d" % len(self.g.joined_players))

    def stop(self):
        self.mqtt.stop()

if __name__ == '__main__':
    sh = SpacehackHost()
    def signal_handler(sig, frame):
        print('Exit')
        sh.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    sh.main()
    sh.gamestart_loop()
    while True:
        signal.pause()
