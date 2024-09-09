from logging import (Handler, 
                     Formatter, 
                     LogRecord, 
                     getLogger,
                     DEBUG,
                     INFO,
                     WARNING,
                     ERROR,
                     CRITICAL)
from logging.config import dictConfig
from .databaseManager import db
import time
import os
import datetime as dt
from json import dumps
from flask import request

class ColourFormatter(Formatter):
    reset = "\x1b[0m"
    white = "\x1b[39m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    orange = "\x1b[38;5;208m"
    red = "\x1b[31"
    colour_dict = {DEBUG:white,
                   INFO:green,
                   WARNING:yellow,
                   ERROR:orange,
                   CRITICAL:red}

    def format(self, record: LogRecord):
        return str(self.colour_dict[record.levelno] + f"[{time.asctime()}] {record.levelname}: {super().format(record)}" + self.reset)

class JsonFormatter(Formatter):
    def is_jsonable(self, obj: object):
        try:
            dumps(obj)
            return True
        except (TypeError, OverflowError):
            return False
        
    def format(self, record):
        record_dict = record.__dict__
        for key, item in record_dict.items():
            if self.is_jsonable(item):
                continue
            else:
                record_dict[key] = repr(item)
        return dumps(record_dict)

class SqlHandler(Handler):
    def emit(self, record: LogRecord):
        if "userid" in record.__dict__ and "action" in record.__dict__:
            try:
                userid = record.userid
                action = record.action
                try:
                    ip = request.remote_addr
                    agent = request.user_agent
                except:
                    ip = None
                    agent = None
            except:
                print(f"error in logging user log {record}")
                return
            db.query("INSERT INTO logs (user_id, action, message, time, ip, agent) VALUES (?, ?, ?, ?, ?, ?)", 
                     (userid, action, record.message.replace("\x1b[33m", "").replace("\x1b[0m",""), 
                      dt.datetime.now().isoformat().replace("T"," "), ip, str(agent)))

log_file_path = os.path.join(os.getcwd(), 'app.jsonl')

dict = {
'version': 1,
'formatters': {
        'default': {'()':ColourFormatter},
        'sql': {'format': '%(message)s'},
        'json': {'()':JsonFormatter}
    },
'handlers': {
    'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }, 
    'sql': {
        '()': SqlHandler, 
        'formatter':'sql'
    },
    'file': {
        'class': 'logging.handlers.RotatingFileHandler',
        'formatter': 'json',
        'filename': log_file_path,
        'mode': 'a',
        'maxBytes': 5 * (1024 ** 2), 
        'backupCount': 3,
        'encoding': 'utf-8'
    },
},
'root': {
    'level': 'INFO',
    'handlers': ['wsgi', 'sql', 'file']
}       
}
dictConfig(dict)
logger = getLogger()