import typer
from quotebook.config import load_config
from quotebook.app import App

def run(host: str="0.0.0.0", port: int=5000, debug: bool = True, config_path:str=""):
    App.config = load_config(path=config_path)
    host = host or App.config["host"]
    port = port or App.config["port"]
    debug = debug or App.config["debug"]
    socket, flask_app = App()
    socket.run(flask_app, host, port, debug=debug)
    
if __name__ == "__main__":
    typer.run(run)