from __future__ import unicode_literals

import json
import time
import sys
import yaml
import os
import importlib
import inspect

from rasahub.messagehandler import RasahubHandler
from rasahub.plugin import RasahubPlugin

def main():
    """The main function initializes plugins and handles messages.
    It starts the messagehandler, registers all plugins and starts the threads.
    When a Keyboard interruption is registered it starts closing all threads.

    """
    messagehandler = RasahubHandler()
    configpath = "config.yml"
    config = yaml.safe_load(open(configpath))

    for plugin in config:
        try:
            lib = __import__(config[plugin]['package'])
            classes = inspect.getmembers(lib, inspect.isclass)
            method = None
            for plugin_class in classes:
                if plugin_class[1].__bases__[0].__name__ == 'RasahubPlugin':
                    method = plugin_class[0]
            if method == None:
                raise Exception
            globals()[plugin] = lib
        except:
            print("Package " + config[plugin]['package'] + " not found.")
        try:
            if config[plugin]['init'] is not None:
                plugin_instance = eval(plugin + '.' + method)(**config[plugin]['init'])
            else:
                plugin_instance = eval(plugin + '.' + method)()
            if plugin_instance is not None:
                plugin_instance.add_target(config[plugin]['out']) # depracted
                messagehandler.add_plugin(plugin, config[plugin]['type'], plugin_instance)
            else:
                print("plugin " + plugin + "could not be started")
        except:
            print("plugin " + plugin + " could not be started")

    messagehandler.start()

    print("Input threads started")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Closing worker threads..")
        messagehandler.end_processes()
        return True
