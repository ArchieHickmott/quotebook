from quotebook import create_app 

socketio, app = create_app(config_path="config.toml")
socketio.run(app, 
             "0.0.0.0", 
             5000,
             use_reloader=True,
             debug=False,
             allow_unsafe_werkzeug=True)