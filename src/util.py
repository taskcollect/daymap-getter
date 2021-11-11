import json


def preprocess_json(inp):
    if isinstance(inp, dict):
        return inp

    try:
        return json.loads(inp)
    except:
        raise ValueError('not a dict')
