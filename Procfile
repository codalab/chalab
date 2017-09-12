web: gunicorn chalab.wsgi --log-file=- --log-level=info
worker: celery -A chalab.chacelery worker --loglevel=info