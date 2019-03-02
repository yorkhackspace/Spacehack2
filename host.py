#!/usr/bin/env python
from paho.mqtt import client as mqtt
import signal
import sys

class MqttWrapper:
    def __init__(self, address='localhost', port=1883):
        self.address = address
        self.port = port
        
    def on_connect(self, client, userdata, flags, rc):
        print("connected to mqqtt")

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
        self.mqtt.message_callback_add(topic, callback)

class SpacehackHost:

    def __init__(self, mqtt=MqttWrapper()):
        self.mqtt = mqtt

    def test_topic(self, client, userdata, message):
        print(message)

    def main(self):
        self.mqtt.connect()
        self.mqtt.sub('test', self.test_topic)

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
    while True:
        signal.pause()
