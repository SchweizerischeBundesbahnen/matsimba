import ConfigParser
import os
import sys


def load():
    config = ConfigParser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
    config.read(config_path)
    sys.path.append(config.get("Modules", "ViPy"))
