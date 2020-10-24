import argparse


# def check_email(email):
#     # match = re.match("^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$", email)
#     if match is None:
#         raise ValueError
#     else:
#         return email


def check_domain(domain):
    if domain == 'eu' or domain == 'com':
        return domain
    else:
        raise ValueError


def check_token(token):
    if token.startswith('1000.') and len(token) == 70:
        return token
    else:
        raise ValueError


def check_client_id(client_id):
    if client_id.startswith('1000.') and len(client_id) == 35:
        return client_id
    else:
        raise ValueError


def check_client_secret(client_secret):
    if len(client_secret) == 42:
        return client_secret
    else:
        raise ValueError


def init_parser():
    parser = argparse.ArgumentParser(description='ga_zoho_config')

    parser.add_argument('-e', action="store", dest="email", type=str, required=True)
    parser.add_argument('-gt', action="store", dest="grant_token", type=check_token, required=True)
    parser.add_argument('-cid', action="store", dest="client_id", type=check_client_id, required=True)
    parser.add_argument('-csec', action="store", dest="client_secret", type=check_client_secret, required=True)
    parser.add_argument('-d', action="store", dest="domain", default='com', type=check_domain)
    parser.add_argument('-nu', action="store", dest='notify_url', type=str, required=True)
    # parser.add_argument('tid', action="store", dest="ga_tid", required = True )

    return parser
