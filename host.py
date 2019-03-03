#!/usr/bin/env python
from paho.mqtt import client as mqtt
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

class Service:
    def __init__(self, func, args, kwargs):
        self.stopped = Event()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def stop(self):
        self.stopped.set()

    def wait(self, *args):
        self.svc_thread.join(*args)

    def start(self):
        def run():
            self.func(*self.args, self.stopped, **self.kwargs)
        self.svc_thread = Thread(target=run)
        self.svc_thread.start()

def service(func):
   def service_wrapper(*args, **kwargs):
       s = Service(func, args, kwargs)
       return s
   return service_wrapper

class Lobby:
    def __init__(self, mqtt):
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

    @service
    def get_service(self, stop_event):
        self.mqtt.connect()
        lc = LobbyConfiguration
        self.gamestarter = GameStarter(lc.GAME_START_DELAY, lc.JOIN_GAME_DELAY, lc.LEAVE_GAME_DELAY)
        self.mqtt.sub('spacehack/+/join', self.handle_join)

        while(not stop_event.isSet()):
            stop_event.wait(0.05)
            self.gamestarter.step_time(0.05)
            if(self.gamestarter.should_start):
                self.mqtt.pub('spacehack/start', ','.join(self.gamestarter.joined_players))
                self.gamestarter.reset()

class SpacehackHost:
    def __init__(self, mqtt=MqttWrapper()):
        self.mqtt = mqtt
        self.lobby = Lobby(mqtt).get_service() #FIXME: Should be a separate object

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
