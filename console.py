from mqtt_wrapper import MqttWrapperFactory
from services import Service

#TODO this file is not ready yet

class Lobby(Service):
    def __init__(self, mqtt_factory, console_id):
        super(Lobby, self).__init__()
        self.mqtt = mqtt_factory.new()
        self.game_id = None
        self.cid = console_id

    def handle_start(self, topic, payload):
        gid, *consoles = payload.split(',')
        print('Game is starting with consoles %r: %s' % (consoles, self.game_id))
        if self.cid in consoles:
            # This is a game that I should join!
            self.game_id = gid
            self.mqtt.pub('/'.join([self.game_id, self.cid, 'ready']), 'ready')
            # TODO start game service

    def init(self):
        self.mqtt.connect()
        self.mqtt.sub('start', self.handle_start)

    def run(self):
        while(not self.stopped.isSet()):

    def cleanup(self):
        self.mqtt.stop()

class SpacehackConsole:
    def __init__(self, console_id, mqtt_factory=SpacehackFactory.mqtt_factory()):
        self.mqtt_factory=mqtt_factory
        self.cid = console_id
        self.lobby = Lobby(self.mqtt_factory, self.cid)

    def stop(self):
        Service.stop_all()
        Service.wait_all()

    def start(self):
        self.lobby.start()

    def wait(self):
        Service.wait_all()

if __name__ == '__main__':
    sh = SpacehackConsole()
    def signal_handler(sig, frame):
        print('Exit')
        sh.stop()
        sh.wait()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    sh.start()
    sh.wait()
