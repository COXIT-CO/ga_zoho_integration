"""Configuration module for logging"""
import logging
from os import mkdir

def mkdir_log():
    try:
        mkdir("./logs")
    except OSError:
        print"Logs directory exists."
    else:
        print"Successfully created the logs directory"
    return "./logs"
LOG_CONFIG = dict(
    version=1,
    formatters={
        'simple':
            {
                'format': '[%(asctime)s] [%(levelname)s] - : %(message)s.',
                'datefmt': '%H:%M:%S',
            },
        'detailed':
            {
                'format': '[%(asctime)s] [%(levelname)s] - Line: %(lineno)d '
                          '- %(name)s - : %(message)s.',
                'datefmt': '%d/%m/%y - %H:%M:%S',
            },
    },
    handlers={
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': logging.INFO,
        },
        'file':
            {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'detailed',
                'level': logging.INFO,
                'filename': mkdir_log()+'logfile',
                'when': 'midnight',
            },
    },
    root={
        'handlers': ['file', ],
        'level': logging.INFO,

    },
)

