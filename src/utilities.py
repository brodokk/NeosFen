import os
import re
import json
import dataclasses
import pathlib

from webcolors import name_to_hex

from kivy.lang import Builder

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)

class CollisionsList(list):
    def get(self, field, value):
        for login in self:
            if getattr(login, field) == value:
                return login
        return None

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
    #print(sessionName)
    # TODO: make a better translator
    sessionName = sessionName.replace('<br>', '')
    sessionName = re.sub(r'<br>', r'', sessionName)
    m = re.findall('<color=(.*?)>', sessionName)
    if m:
        for color in m:
            if not color.startswith('#'):
                sessionName = re.sub(r'<color=' + color + '>', '[color=' + name_to_hex(color) + ']', sessionName)
            else:
                sessionName = re.sub(r'<color=' + color + '>', '[color=' + color + ']', sessionName)
        sessionName = re.sub(r'</color>', r'[/color]', sessionName)
    sessionName = re.sub(r'</b>', r'[/b]', sessionName)
    sessionName = re.sub(r'<b>', r'[b]', sessionName)
    return sessionName

def load_kv_files(path):
    # Gets current python dir then add the KV dir
    kv_path = pathlib.Path.cwd() / path
    #kv_load_list = [f for f in os.listdir(kv_path) if os.path.isfile(os.path.join(kv_path, f))]
    kv_load_list = [f for f in kv_path.rglob("**/*") if (kv_path / f).isfile()] 

    # Loads all KV file
    for file in kv_load_list:
        if file.endswith('.kv'):
            Builder.load_file(kv_path / file)
