from typing import Tuple
import os

from flask_socketio import SocketIO
from flask import Flask

from quotebook.app import App
from quotebook.config import load_config

def create_app(host:str=None, port:int=None, debug:bool|None=None, config_path:str="") -> Tuple[SocketIO, Flask]:
    if config_path:
        App.config = load_config(path=config_path)
        host = host or App.config["host"]
        port = port or App.config["port"]
        debug = debug or App.config["debug"]
    else:
        App.config["secret_key"] = os.urandom(128)
        App.config["session_time"] = 3600
        App.config["public_endpoints"] = ["accounts.login", "accounts.register", "landing", "privacy", "terms"]
    socket, flask_app = App()
    return socket, flask_app