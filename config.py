from configparser import ConfigParser
import os

CONFIG_FILENAME = 'config.ini'

class Config:
    def __init__(self, env):
        self.path = os.path.join(os.getcwd(), CONFIG_FILENAME)
        self.env = env
        self.config = self.__read(self.path)

    def getboolean(self, key):
        return self.config.getboolean(self.env, key)

    def __read(self, path):
        config = ConfigParser()
        config.read(path)

        return config