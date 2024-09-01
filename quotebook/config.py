""" 
current toml template:

debug = 
host = 
port = 
public_endpoints =
secret_key = 
session_time = 
"""

import tomllib
import os

default_toml = """
debug = true
host = '0.0.0.0'
port = 5000
public_endpoints = ["accounts.login", "accounts.register", "landing"]
session_time = 3600
"""

configs = ["debug", "host", "port", "public_endpoints", "secret_key", "session_time"]

def load_config(tomls: str = "", path: str = ""):
    default_config = tomllib.loads(default_toml)
    if tomls:
        config = tomllib.loads(tomls)
    if path:
        with open(path, "rb") as f:
            config = tomllib.load(f)
    else:
        return default_config
    
    for key in config.keys():
        if not key in configs:
            config.pop(key)
    for key in configs:
        value = config.get(key, None)
        if value is None:
            value = default_config.get(key, None)
        config[key] = value
    
    if config["secret_key"] is None:
        config["secret_key"] = os.urandom(128)
        
    print(config)
    return config