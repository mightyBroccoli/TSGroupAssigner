# -*- coding: utf-8 -*-
import json

with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)


class Config(object):
    # connection arguments
    HOST = config['host']
    PORT = config['port']
    USER = config['user']
    PW = config['password']
    SID = config['server_id']

    # assignment settings
    GID = config['gid']
