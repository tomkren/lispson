import json
from collections import OrderedDict


def ordered_dumps(json_o):
    # json_str = json.dumps(json_o)
    # data = json.loads(json_str, object_pairs_hook=OrderedDict)
    return json.dumps(json_o, sort_keys=True)


def json_eq(json_o1, json_o2):
    return ordered_dumps(json_o1) == ordered_dumps(json_o2)
