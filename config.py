"""Configuration module for logging"""
import argparse
import errno
import logging
import sys
from logging.config import dictConfig
from os import makedirs, symlink
from pyngrok import ngrok


class AppConfig:
    def __init__(self):
        parser = self.create_parser()
        self.args = parser.parse_args(sys.argv[1:])
        self.port = self.args.port
        self.notify_url = self.ngrok_settings(self.args.ngrok_token, self.port)
        self.logger = self.init_logger(self.args)
        self.ZOHO_NOTIFICATIONS_ENDPOINT = "/zoho/deals/change"

    def create_parser(self):
        """Creat parameters passing from console"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-e', '--email')
        parser.add_argument('-gt', '--grant_token')
        parser.add_argument('-cid', '--client_id')
        parser.add_argument('-cs', '--client_secret')
        parser.add_argument('-api', '--api_uri', default='com')
        parser.add_argument('-ngrok', '--ngrok_token')
        parser.add_argument('-port', '--port', default='80')
        parser.add_argument('-logmode', '--logmode', default='file')
        parser.add_argument('-logpath', '--logpath', default='./logs')
        return parser

    def ngrok_settings(self, token, port):
        """configure ngrok settings"""
        ngrok.set_auth_token(token)
        return str(ngrok.connect(port=port))

    def init_logger(self, args):
        log_path = self.init_logdir(args.logpath)
        flask_log = logging.getLogger('werkzeug')
        flask_log.setLevel(logging.ERROR)
        dictConfig(self.init_log_config(log_path, args.logmode))
        _logger = logging.getLogger()
        return _logger

    def init_logdir(self, logpath):
        """create log directory and symbolic link"""
        dest = '/home/ga_zoho_logs'
        try:
            makedirs(logpath)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                logging.exception("Problems with creating log directory", exc_info=ex)
                self.init_logdir('./logs')
            else:
                print "Log directory already created at " + logpath
                # symlink(logpath, dest)
                return logpath
        else:
            print "Successfully created the logs directory at: \n" + logpath
            # symlink(logpath, dest)
            return logpath

    def init_log_config(self, log_dir, handlers):
        """initialize log config dictionary"""
        return dict(
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
                        'filename': log_dir + 'logfile',
                        'when': 'midnight',
                    },
            },
            root={
                'handlers': ['file', ].append(handlers),
                'level': logging.INFO,
            },
        )
