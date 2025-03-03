import json


class JsonConvert(object):
    mappings = {}

    @classmethod
    def class_mapper(clsself, d):
        for keys, cls in clsself.mappings.items():
            if keys.issuperset(d.keys()):  # are all required arguments present?
                return cls(**d)
        else:
            # Raise exception instead of silently returning None
            raise ValueError('Unable to find a matching class for object: {!s}'.format(d))

    @classmethod
    def complex_handler(clsself, Obj):
        if hasattr(Obj, '__dict__'):
            return Obj.__dict__
        else:
            raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(Obj), repr(Obj)))

    @classmethod
    def register(clsself, cls):
        clsself.mappings[frozenset(tuple([attr for attr, val in cls().__dict__.items()]))] = cls
        return cls

    @classmethod
    def to_json(clsself, obj):
        return json.dumps(obj.__dict__, default=clsself.complex_handler, indent=4)

    @classmethod
    def from_json(clsself, json_str):
        return json.loads(json_str, object_hook=clsself.class_mapper)

    @classmethod
    def to_file(clsself, obj, path):
        with open(path, 'w') as jfile:
            jfile.writelines([clsself.to_json(obj)])
        return path

    @classmethod
    def from_file(clsself, filepath):
        result = None
        with open(filepath, 'r') as jfile:
            result = clsself.from_json(jfile.read())
        return result
