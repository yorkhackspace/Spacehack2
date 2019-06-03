import os
from functools import wraps
from paho.mqtt import client as mqtt

# I dunno Bart, my dad's a really big wheel down at the WrapperFactory
class MqttWrapperFactory:
    def __init__(self, address='localhost', port=1883, topic_prefix=''):
        def new(subtopic=''):
            return MqttWrapper(address, port, MqttWrapper.fixup_slash(topic_prefix + subtopic))
        self.new = new

class MqttWrapper:
    def __init__(self, address, port, topic_prefix):
        self.mqtt = None
        self.address = address
        self.port = port
        self.topic_prefix = topic_prefix

    def fixup_slash(text):
        newtext = '/'.join(p for p in text.split('/') if p != '')
        if newtext[-1] != '#':
            newtext += '/'
        return newtext

    def full_topic(self, subtopic):
        return MqttWrapper.fixup_slash(self.topic_prefix + subtopic)

    def on_connect(self, client, userdata, flags, rc):
        pass
        #print("connected to mqtt")

    def check_connection(self):
        if self.mqtt is None:
            raise Exception("MqttWrapper.connect() not yet called")

    def connect(self):
        self.mqtt = mqtt.Client()
        self.mqtt.on_connect = self.on_connect
        self.mqtt.connect(self.address, self.port, 60)
        self.mqtt.loop_start()

    def stop(self):
        self.mqtt.loop_stop()
        self.mqtt.disconnect()

    def sub(self, topic, callback):
        self.check_connection()
        full_topic = self.full_topic(topic)
        self.mqtt.subscribe(full_topic)
        wrapped_callback = self.wrap_message_handler(callback)
        self.mqtt.message_callback_add(full_topic, wrapped_callback)

    def wrap_message_handler(self, callback):
        @wraps(callback)
        def message_handler_wrapper(client, userdata, message):
            return callback([s for s in message.topic.split('/') if s != ''], message.payload.decode('utf-8'))
        return message_handler_wrapper

    def pub(self, topic, payload):
        self.check_connection()
        self.mqtt.publish(self.full_topic(topic), payload)

    def dump(self, topic, payload):
        print("%s: %s" % (topic, payload))
