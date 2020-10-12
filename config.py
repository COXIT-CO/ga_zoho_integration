import logging

logging_config = dict(
    version=1,
    formatters={
        'f': {'format':
                  '[%(levelname)s] - Line: %(lineno)d - %(name)s - : %(message)s.'}
    },
    handlers={
        'h': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.ERROR}
    },
    root={
        'handlers': ['h'],
        'level': logging.ERROR,
    },
)
