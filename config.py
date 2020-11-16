"""Configuration module for logging"""
import errno
import logging
from os import makedirs

LOG_DIR = ""

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
                'filename': LOG_DIR+'logfile',
                'when': 'midnight',
            },
    },
    root={
        'handlers': ['file', ],
        'level': logging.INFO,
    },
)

def init_logdir(logpath):
    global LOG_DIR
    try:
        makedirs(logpath)
    except OSError as ex:
        if ex.errno != errno.EEXIST:
           logging.exception("Problems with creating log directory", exc_info=ex)
	   init_logdir('./logs')
        else:
           print('Log directory already created at ' + logpath)
    else:
  	 print("Successfully created the logs directory at: \n"+logpath)
    LOG_DIR = logpath
