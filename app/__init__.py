from app.app import app

def main(host:str="0.0.0.0", port:int=5000, debug:bool|None=None):
    app.run(host, port, debug)