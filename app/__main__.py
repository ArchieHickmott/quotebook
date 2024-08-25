import typer

from .app import app

def run(host: str="0.0.0.0", port: int=5000, debug: bool = True):
    app.run(host, port, debug)
    
if __name__ == "__main__":
    typer.run(run)