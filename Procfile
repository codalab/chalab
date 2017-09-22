web: gunicorn chalab.wsgi --log-file=- --log-level=info -k gevent
worker: celery -A chalab.chacelery worker --loglevel=info