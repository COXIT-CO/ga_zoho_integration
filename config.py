# pylint: disable=import-error
# pylint: disable=relative-import
"""Configuration module for logging"""
import errno
import logging
import logging.handlers
import configparser
from os import makedirs, symlink
from pyngrok import ngrok
from setup import CONFIG_FILE


class AppConfig(object):
    """Class for configuring app"""
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)

        self.port = config['ngrok']['port']
        self.zoho_notification_endpoint = "/zoho/deals/change"
        self.ngrok_url = self.ngrok_run(config['ngrok']['token'], self.port)
        self.init_logger(config['logging'])

    @staticmethod
    def ngrok_run(token, port):
        """Run ngrok and return public url"""
        ngrok.set_auth_token(token)
        return str(ngrok.connect(port=port))

    def init_logger(self, log_config):
        """creates app logger and configures it"""
        logger = logging.getLogger('app')
        log_level = logging.INFO
        if log_config['debug']:
            log_level = logging.DEBUG
        logger.setLevel(log_level)
        log_path = self.init_logdir(log_config['logpath'])
        self.create_symlink(log_path)
        log_path += '/'
        detailed_formatter = logging.Formatter(fmt='[%(asctime)s] [%(levelname)s] - '
                                                   'Line: %(lineno)d - %(name)s - : %(message)s.',
                                               datefmt='%H:%M:%S')

        file_handler = logging.handlers.TimedRotatingFileHandler(log_path + 'logfile',
                                                                 when='midnight')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

        if log_config['logmode'] == 'console':
            simple_formatter = logging.Formatter(fmt='[%(asctime)s] [%(levelname)s] - : '
                                                     '%(message)s.',
                                                 datefmt='%H:%M:%S')
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(simple_formatter)
            logger.addHandler(console_handler)

        flask_log = logging.getLogger('werkzeug')
        flask_log.setLevel(logging.ERROR)
        root_h = logging.root.handlers[0]
        logging.root.removeHandler(root_h)

    def init_logdir(self, logpath):
        """create log directory and symbolic link"""
        try:
            makedirs(logpath)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                logging.exception("Problems with creating log directory", exc_info=ex)
                self.init_logdir('./logs')
            else:
                logging.info("Log directory already created at %s", logpath)
                return logpath
        else:
            logging.info("Successfully created the logs directory at: \n%s", logpath)
            return logpath

    @staticmethod
    def create_symlink(logpath):
        """creates symbolic link for directory"""
        dest = '/home/ga_zoho_logs'
        try:
            symlink(logpath, dest)
        except OSError as ex:
            if ex.errno != errno.EEXIST:
                logging.exception("Problems with creating log directory. Symlink is not created",
                                  exc_info=ex)
            else:
                logging.info("Symlink is already created at %s", dest)
