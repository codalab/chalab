from chalab.settings import *


def clearl(xs):
    return [x.strip() for x in xs]


DEBUG = False
SECRET_KEY = os.environ['CHALAB_SECRET_KEY'].strip()
ALLOWED_HOSTS = clearl(os.environ['CHALAB_ALLOWED_HOSTS'].split(','))

