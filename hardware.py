from config import ConfigError

class Component:
    """ Base class for hardware components"""
    def __init__(self, config, callback=None):
        self.config = config
        self.callback = callback

    def set_callback(self, callback):
        self.callback = callback

    def connect(self):
        raise NotImplemented("connect should be implemented by subcalsses of Component")

    def from_config(config, callback=None):
        if 'type' not in config:
            raise ConfigError("No type defined for this component")
        component_class = {
            'button': Button,
        }.get(config['type'])
        if component_class is None:
            raise ConfigError("Unknown hardware component type %s" % (config['type']))
        return component_class(config, callback=callback)

    def poll():
        pass

class Button(Component):
    def connect(self):
        pass
        # TODO read the config and figure out how
        # to set an interrupt (or to start polling)
        # which calls self.state_callback

    def poll():
        pass
