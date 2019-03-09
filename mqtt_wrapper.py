import os
from functools import wraps
from paho.mqtt import client as mqtt

class MqttWrapper:
    def __init__(self, address='localhost', port=1883, topic_prefix='spacehack/'):
        self.address = address
        self.port = port
        self.topic_prefix = topic_prefix
        override = 'SH_TOPIC_PREFIX_OVERRIDE'
        if override in os.environ:
            prefix = os.environ[override]
            self.topic_prefix = ''.join(c if c not in '\/.#$+_' else '-' for c in os.environ[override]) + '/'

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
        full_topic = self.topic_prefix + topic
        self.mqtt.subscribe(full_topic)
        wrapped_callback = self.wrap_message_handler(callback)
        self.mqtt.message_callback_add(full_topic, wrapped_callback)

    def wrap_message_handler(self, callback):
        @wraps(callback)
        def message_handler_wrapper(client, userdata, message):
            return callback(message.topic, message.payload.decode('utf-8'))
        return message_handler_wrapper

    def pub(self, topic, payload):
        self.mqtt.publish(self.topic_prefix + topic, payload)

    def dump(self, topic, payload):
        print("%s: %s" % (topic, payload))

