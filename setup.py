import sys
import argparse
import configparser
from os import path

CONFIG_FILE = 'Settings.ini'


def create_parser():
    """Create parameters passing from console"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--email')
    parser.add_argument('-gt', '--grant_token', default=' ')
    parser.add_argument('-cid', '--client_id')
    parser.add_argument('-cs', '--client_secret')
    parser.add_argument('-api', '--api_uri', default='com')
    parser.add_argument('-ngrok', '--ngrok_token')
    parser.add_argument('-port', '--port', default='80')
    parser.add_argument('-logmode', '--logmode', default='file')
    parser.add_argument('-logpath', '--logpath', default='./logs')
    parser.add_argument('-debug', '--debug', action='store_true')
    return parser


def initialize_variables():
    """Using parser to output parameters from console"""
    config = configparser.ConfigParser()
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    config.add_section('Zoho')

    if namespace.grant_token:
        config['Zoho']['grant_token'] = namespace.grant_token

    config['Zoho']['client_id'] = namespace.client_id
    config['Zoho']['client_secret'] = namespace.client_secret
    config['Zoho']['email'] = namespace.email
    config['Zoho']['api'] = namespace.api_uri

    config.add_section('ngrok')
    config['ngrok']['token'] = namespace.ngrok_token
    config['ngrok']['port'] = namespace.port

    config.add_section('logging')
    config['logging']['logmode'] = namespace.ngrok_token
    config['logging']['logpath'] = namespace.logpath
    config['logging']['debug'] = namespace.port

    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)


if __name__ == '__main__':
    if path.isfile(CONFIG_FILE):
        key = raw_input("Do you really wanna change your settings?(y/n) ")
        if key == "y":
            initialize_variables()
        else:
            sys.exit("Script is terminated")
    else:
        initialize_variables()
