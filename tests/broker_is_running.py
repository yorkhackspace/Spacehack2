# RUN: python %s
from paho.mqtt import client as mqtt
m = mqtt.Client()
m.connect('localhost', 1883, 60)
