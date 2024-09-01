from quotebook.app import App
from quotebook.config import load_config

def main(host:str=None, port:int=None, debug:bool|None=None, config_path:str=""):
    App.config = load_config(path=config_path)
    host = host or App.config["host"]
    port = port or App.config["port"]
    debug = debug or App.config["debug"]
    socket, flask_app = App()
    socket.run(flask_app, host, port, debug=debug)