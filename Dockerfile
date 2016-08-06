FROM python:3.5

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app

# Install the gunicorn server to serve django
RUN pip install gunicorn==19.6.0

# Install the dependencies (rarely change)
ADD requirements.txt /app
RUN pip install -r requirements.txt

# Install the app code (change often)
ADD . /app
