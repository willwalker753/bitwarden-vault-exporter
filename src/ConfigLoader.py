import os

class ConfigLoader:
    def __init__(self):
        pass

    def get(self, key):
        value = os.getenv(key)
        if value == None:
            raise Exception(f'Missing required env variable: {key}')
        return value