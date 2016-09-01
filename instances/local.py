import subprocess

from chalab.settings import *

import os

import sys; print(os.environ['PATH'], file=sys.stderr)

CMD_GET_DB_IP_PORT = """docker port chalab_db_1 5432"""
_db_ip = subprocess.check_output(CMD_GET_DB_IP_PORT, shell=True)
host, port = _db_ip.decode('utf-8').strip().split(':')

DATABASES['default']['HOST'] = host
DATABASES['default']['PORT'] = port

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

