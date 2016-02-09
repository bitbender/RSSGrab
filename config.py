import yaml


class Config(object):
    """
    This class implements a config holder. The holder is responsible for
    loading the current configuration from a YAML file and by doing so
    making the configuration accessable.

    The config holder implements the singleton design pattern.
    """
    _instance = None

    def __init__(self, file):
        """
        The constructor of this class.

        It creates a Config object that contains all the config
        parameters defined in the config file or, if no config
        file is specified, a Config object that is empty

        :param file: a file from which to load the configuration
        """

        if Config._instance is not None:
            raise NotImplemented("This is a singleton class. Use the get_instance() method")

        if file:
            self.file = file
            with open(file, 'r') as ymlfile:
                self.config = yaml.load(ymlfile)
        else:
            self.config = {}

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
        """
        This method loads a config file into the Config object

        :param file: a file that should be loaded into the config object
        """
        self.file = file
        with open(file, 'r') as ymlfile:
            self.config = yaml.load(ymlfile)

    def save(self):
        """
        This method saves the config object to a config file.
        :return:
        """
        with open(self.file, 'w') as ymlfile:
            ymlfile.write(yaml.dump(self.config))

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
