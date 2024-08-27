import typer

from app.config import socket, flask_app

def run(host: str="0.0.0.0", port: int=5000, debug: bool = True):
    socket.run(flask_app, host, port, debug=debug)
    
if __name__ == "__main__":
    typer.run(run)