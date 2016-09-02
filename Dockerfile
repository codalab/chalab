FROM python:3.5

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /app/ /app/static
WORKDIR /app
CMD ["/usr/local/bin/gunicorn", "chalab.wsgi:application", "-w 2", "-b :8000"]

# Install the gunicorn server to serve django
RUN pip install gunicorn==19.6.0

# Install the dependencies (rarely change)
ADD requirements.txt /app
RUN pip install -r requirements.txt

# Install the app code (change often)
ADD . /app

# Generate statics
RUN python manage.py collectstatic --noinput

VOLUME "/app/static"
VOLUME "/app/media"
