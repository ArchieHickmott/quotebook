from app.config import flask_app

def main(host:str="0.0.0.0", port:int=5000, debug:bool|None=None):
    flask_app.run(host, port, debug)