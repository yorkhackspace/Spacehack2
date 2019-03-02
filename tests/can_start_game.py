# RUN: python %s

import sys
import time
import threading
from host import SpacehackHost, MqttWrapper
from paho.mqtt import client as mqtt

sh = SpacehackHost()
sh.main()

c = MqttWrapper()
c.connect()

done = False

def start(client, userdata, message):
    global done
    print("Start game")
    assert message.payload.decode('utf-8') == '2'
    done = True

c.sub('spacehack/start', start)

threading.Thread(target=sh.gamestart_loop).start()

c.pub('spacehack/1/join', '1')
c.pub('spacehack/2/join', '1')

time.sleep(15)
if not done:
    sys.exit(1)
