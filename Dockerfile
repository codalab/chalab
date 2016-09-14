FROM python:3.5

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /app/ /app/static /app/media /app/datasets
WORKDIR /app
CMD ["/usr/local/bin/gunicorn", "chalab.wsgi:application", "-w 2", "-b :8000"]

# Install the gunicorn server to serve django
RUN pip install gunicorn==19.6.0

# Install the dependencies (rarely change)
ADD requirements.txt /app
RUN pip install -r requirements.txt

# Install the app code (change often)
ADD . /app

# This is not ideal, we chmod so that the celery container (running non root)
# can write to the media folder (for outputs).
# TODO(laurent): Use groups to avoid chmoding for the whole world, or use
#  data volumes.
RUN chmod -R 777 /app/media

# Generate statics
RUN python manage.py collectstatic --noinput

VOLUME "/app/static"
VOLUME "/app/media"
