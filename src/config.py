import os
import yaml

class Config(dict):
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self._yaml = f.read()
            self._dict = yaml.load(self._yaml)
            self._dict['PATH'] = os.path.dirname(config_path)
 
    def __getattr__(self, name):
        if self._dict.get(name) is not None:
            return self._dict[name]

        if DEFAULT_CONFIG.get(name) is not None:
            return DEFAULT_CONFIG[name]

        return None

    def print(self):
        print('Model configurations:')
        print('---------------------------------')
        print(self._yaml)
        print('')
        print('---------------------------------')
        print('')


DEFAULT_CONFIG = {
    'MODE': 2,                      # 1: train, 2: test, 3: eval, 5: drawing
    'SEED': 10,                     # random seed
    'GPU': [0],                     # list of gpu ids
    'DEBUG': 0,                     # turns on debugging mode
    'VERBOSE': 0,                   # turns on verbose mode in the output console

    'INPUT_SIZE': 128,              # input image size for training 0 for original size
    'SIGMA': 2.5,                     # standard deviation of the Gaussian filter used in Canny edge detector (0: random, -1: no edge)
    'KM': 3,
}