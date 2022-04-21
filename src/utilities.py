import os
import sys
import re
import json
import dataclasses
import pathlib
from datetime import datetime

from webcolors import name_to_hex

from kivy.lang import Builder

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            data = dataclasses.asdict(o)
            for key, value in data.items():
                if type(value) == datetime:
                    data[key] = value.isoformat()
            return data
        return super().default(o)

class CollisionsList(list):
    def get(self, field, value):
        for login in self:
            if getattr(login, field) == value:
                return login
        return None

    def update(self, search_field, search_value, field, value):
        for i in range(len(self)):
            if getattr(self[i], search_field) == search_value:
                setattr(self[i], field, value)
                return True
        raise ValueError('--> No value {0} found for field {1}'.format(search_value, search_field))

    def contains(self, field, value):
        for login in self:
            if getattr(login, field) == value:
                return True
        return False

    def append(self, other, field):
        for login in self:
            if getattr(other, field) == getattr(login, field):
                raise ValueError('--> Value already added: {0}'.format(other))
        super().append(other)

def html2bbcode(sessionName):
    # TODO: make a better translator
    sessionName = sessionName.replace('<br>', '')
    sessionName = re.sub(r'<br>', r'', sessionName)
    m = re.findall('<color(?: |=)(.*?)>', sessionName)
    if m:
        for color in m:
            if not color.startswith('#'):
                sessionName = re.sub(r'<color(?: |=)' + color + '>', '[color=' + name_to_hex(color) + ']', sessionName)
            else:
                sessionName = re.sub(r'<color(?: |=)' + color + '>', '[color=' + color + ']', sessionName)
        sessionName = re.sub(r'</color>', r'[/color]', sessionName)
    sessionName = re.sub(r'</b>', r'[/b]', sessionName)
    sessionName = re.sub(r'<b>', r'[b]', sessionName)
    return sessionName

def load_kv_files(path):
    # Gets current python dir then add the KV dir
    if hasattr(sys, '_MEIPASS'):
        kv_path = sys._MEIPASS / path
    else:
        kv_path = pathlib.Path.cwd() / path
    kv_load_list = [f for f in kv_path.rglob("**/*") if (kv_path / f).is_file()]
    # Loads all KV file
    for file in kv_load_list:
        if file.suffix == '.kv':
            Builder.load_file(str(kv_path / file))
