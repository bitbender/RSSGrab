import yaml


class Config(object):
    """
    This class implements a config holder. The holder is responsible for
    loading the current configuration from a YAML file and by doing so
    making the configuration accessable.
    """
    _instance = None

    def __init__(self, file='config.yml'):

        if Config._instance is not None:
            raise NotImplemented("This is a singleton class. Use the get_instance() method")

        with open(file, 'r') as ymlfile:
            self.config = yaml.load(ymlfile)

    @staticmethod
    def get_instance():
        """
        This method returns an instance of the Config class.
        :return: an instance of the Config class.
        """
        if Config._instance is None:
            Config._instance = Config()

        return Config._instance

    def load(self, file):
        with open(file, 'r') as ymlfile:
            self.config = yaml.load(ymlfile)

    def __getitem__(self, item):
        return self.config[item]

    def __setitem__(self, key, value):
        self.config[key] = value

    def __delitem__(self, key):
        del self.config[key]

    def __iter__(self):
        return iter(self.config)

    def __len__(self):
        return len(self.config)

    def __repr__(self):
        return yaml.dump(self.config)
