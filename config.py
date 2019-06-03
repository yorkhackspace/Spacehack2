import os
import toml

class ConfigError(Exception):
    """ Thrown when something from a config file doesn't make sense """
    pass

class CommonConfig:
    """ A class that holds the common base configuration. Normally accessed
    by either `load` or `build` to combine it with other config values """

    def root_topic():
        env_topic = os.environ.get('SH_TOPIC_PREFIX_OVERRIDE') or 'spacehack'
        return ''.join(c if c not in '\/.#$+_' else '-' for c in env_topic) + '/'

    def get():
        return {'root_topic':CommonConfig.root_topic()}

def load(filename):
    """ Load a TOML file and combine it with the default base config
    and return the result as a dictionary """
    conf = CommonConfig.get()
    conf.update(toml.load(filename))
    return conf

def build(**kwargs):
    """ Build a config dict with the default configuration values
    and any config values specified as keyword arguments to this 
    function """
    conf = CommonConfig.get()
    for key, value in kwargs.items():
        conf[key] = value
    return conf
