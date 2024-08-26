import typer

from app.config import flask_app

def run(host: str="0.0.0.0", port: int=5000, debug: bool = True):
    flask_app.run(host, port, debug)
    
if __name__ == "__main__":
    typer.run(run)