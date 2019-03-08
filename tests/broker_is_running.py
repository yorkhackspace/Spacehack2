# RUN: ./tbin/test_coverage.sh %s
from libs.test_utils import TimeoutTest
from paho.mqtt import client as mqtt

m = mqtt.Client()
test = TimeoutTest()

def connected(client, userdata, flags, rc):
    print("connected to mqtt")
    test.passed()

m.on_connect = connected
m.connect('localhost', 1883, 60)
test.run(m.loop_forever, lambda:None)

