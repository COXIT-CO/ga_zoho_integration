"""Configuration module for logging"""
import argparse
import errno
import logging
import logging.handlers
import sys
from os import makedirs, symlink
from pyngrok import ngrok


class AppConfig:
    def __init__(self):
        parser = self.create_parser()
        self.args = parser.parse_args(sys.argv[1:])
        self.port = self.args.port
        self.ZOHO_NOTIFICATIONS_ENDPOINT = "/zoho/deals/change"
        self.ngrok_url = self.ngrok_settings(self.args.ngrok_token, self.port)
        self.init_logger()

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
        parser.add_argument('-debug', '--debug', action='store_true')
        return parser

    def ngrok_settings(self, token, port):
        """configure ngrok settings"""
        ngrok.set_auth_token(token)
        return str(ngrok.connect(port=port))

    def init_logger(self,):
        logger = logging.getLogger('app')
        log_level = logging.INFO
        if self.args.debug:
            log_level = logging.DEBUG
        logger.setLevel(log_level)
        log_path = self.init_logdir(self.args.logpath)+'/'
        detailed_formatter = logging.Formatter(fmt='[%(asctime)s] [%(levelname)s] - '
                                                   'Line: %(lineno)d - %(name)s - : %(message)s.',
                                               datefmt='%H:%M:%S')

        file_handler = logging.handlers.TimedRotatingFileHandler(log_path+'logfile', when='midnight')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

        if self.args.logmode == 'console':
            simple_formatter = logging.Formatter(fmt='[%(asctime)s] [%(levelname)s] - : %(message)s.',
                                                 datefmt='%H:%M:%S')
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(simple_formatter)
            logger.addHandler(console_handler)

        flask_log = logging.getLogger('werkzeug')
        flask_log.setLevel(logging.ERROR)

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
                symlink(logpath, dest)
                return logpath
        else:
            print "Successfully created the logs directory at: \n" + logpath
            symlink(logpath, dest)
            return logpath
