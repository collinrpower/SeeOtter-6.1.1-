import json
from abc import abstractmethod
from os.path import exists
from Utilities.json_convert import JsonConvert


@JsonConvert.register
class SerializableConfigBase:

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls().load()
        return cls._instance

    @abstractmethod
    def get_file_path(self):
        pass

    def save(self, path=None):
        path = path or self.get_file_path()
        JsonConvert.to_file(self, path)

    def load(self, path=None):
        path = path or self.get_file_path()
        if exists(path):
            with open(path, "r") as json_file:
                json_data = json.load(json_file)
                self.__dict__.update(json_data)
        self.save()
        return self

    @classmethod
    def get_default_config(cls):
        if cls._default is None:
            cls._default = cls()
        return cls._default

    @classmethod
    def reset_to_default(cls):
        cls._instance = cls()
        cls._instance.save()
