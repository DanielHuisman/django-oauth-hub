from functools import cache
from importlib import import_module
from typing import Any


def get_by_key_string(data: dict, key: str) -> Any:
    keys = key.split('.')
    for key in keys:
        data = data.get(key, None)
        if data is None:
            break
    return data


@cache
def import_attribute(name: str, attr_type: type = None) -> Any:
    module_name, _, attr_name = name.rpartition('.')
    attr = getattr(import_module(module_name), attr_name)

    if attr_type and not isinstance(attr, attr_type):
        raise ValueError(f'Imported attribute "{name}" should be of type "{attr_type}", but is "{type(attr)}".')

    return attr
