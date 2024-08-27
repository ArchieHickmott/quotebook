from app.config import socket, flask_app

def main(host:str="0.0.0.0", port:int=5000, debug:bool|None=None):
    socket.run(flask_app, host, port, debug=debug)