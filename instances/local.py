import subprocess

from chalab.settings import *


def naive_service_ip(service_name, port):
    cmd = """docker port chalab_%s_1 %s""" % (service_name, port)
    out = subprocess.check_output(cmd, shell=True)
    host, port = out.decode('utf-8').strip().split(':')
    return host, port


# Databaset
# ---------

h, p = naive_service_ip('db', 5432)

DATABASES['default']['HOST'] = h
DATABASES['default']['PORT'] = p

# Email
# -----

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# RabbitMQ
# --------

h, p = naive_service_ip('rabbitmq', 5672)
BROKER_URL = 'amqp://admin:admin@%s:%s/chalab' % (h, p)

# Celery
# ------

CELERY_ALWAYS_EAGER = True # avoid going through the daemon: because test db is not the daemon db.
