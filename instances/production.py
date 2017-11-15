from chalab.settings import *


def clearl(xs):
    return [x.strip() for x in xs]


DEFAULT_FROM_EMAIL='webmaster@chalab'
DEBUG = True
# SECRET_KEY = os.environ['CHALAB_SECRET_KEY'].strip()
SECRET_KEY = os.environ.get('CHALAB_SECRET_KEY')
ALLOWED_HOSTS = clearl(os.environ['CHALAB_ALLOWED_HOSTS'].split(','))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.debug.log',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
