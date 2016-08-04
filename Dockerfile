FROM python:3.5

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app

# Install the dependencies (rarely change)
ADD requirements.txt /app
RUN pip install -r requirements.txt

# Install the app code (change often)
ADD . /app
