import types

import yaml

from yay.loader import Loader
from yay.resolver import Resolver
from yay.ordereddict import OrderedDict

class Config(object):

    def __init__(self, special_term='yay'):
        self.special_term = special_term
        self._raw = {}

    def load_uri(self, uri):
        #FIXME: Eventually support pluggable URI backends, for now treat everything as a file
        self.load(open(uri))

    def load(self, stream):
        data = yaml.load(stream, Loader=Loader)

        special = data.get(self.special_term, None)
        if special:
            for uri in special.get('extends', []):
                self.load_uri(uri)

        self.update(data)

    def update(self, config):
        """
        Recursively update config with a dict
        """
        def recurse(src, target):
            for key, value in src.iteritems():
                if "." in key:
                    key, action = key.split(".")
                else:
                    action = "assign"

                if isinstance(value, dict):
                    recurse(value, target.setdefault(key, {}))
                else:
                    #FIXME: Break this out into some kind of registry
                    if action == "append":
                        target[key] += value
                    elif action == "assign":
                        target[key] = value
                    else:
                        raise KeyError("Unknown action '%s'" % action)

        recurse(config, self._raw)

    def get(self):
        return Resolver(self._raw).resolve()

def load_uri(stream, special_term='yay'):
    c = Config(special_term)
    c.load_uri(uri)
    return c.get()

def load(stream, special_term='yay'):
    c = Config(special_term)
    c.load(stream)
    return c.get()
