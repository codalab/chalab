Chalab
======

Requires:
- docker

For development (running the tests):

- `python3.5`
- an env with the content of the `requirements.txt` (`pip install -r requirements.txt`).
- `phantomjs`, at least, for browser testing.


Structure
---------

- `chalab`: core of the project,
- `landing`: the home page,
- `instances`: the module containing the settings per environment:
    - `local`: the settings to run django on your local machine,
    - `local_docker`: the settings to run django in docker on your local machine (preferred way),
    

Local Dev
---------

The most straightforward way to run chalab is to use docker and docker-compose. It will
start the system (database, server, etc) automatically.

Then you can run the tests on your local machine (non-dockerized) to get assistance from your IDE.
It's also possible to run the tests from inside docker, you wont need any other dependencies
than docker.

### Fully dockerized:

In the chalab folder,

- `docker-compose up web`: It downloads all the containers & dependencies then start the containers.
    Access the app at [http://localhost:8000/](http://localhost:8000/).
- `docker-compose build`: re-build the image (when requirements.txt changed for example).

*db management*

- `docker-compose run web python manage.py migrate`: Apply the database migrations.

*test*

Testing in docker is not supported yet, don't hesitate to take a look and send a Pull Request.


#### Running on local:

With the database running from `docker-compose up`,
`export DJANGO_SETTINGS_MODULE='instances.local'` sets the django configuration in your shell

- `python manage.py runserver 0.0.0.0:8002`: run the server,
   it'll be accessible at [http://localhost:8002](http://localhost:8002).
    
*db management*

- `python manage.py migrate`: Apply the database migrations.

*tests*

- `python manage.py test`: Run the tests
- You can override the selenium ENVs used by `tests/selen.py` to use different drivers,
  by default, you need `phantomjs` installed.
- `chrome` requires the [`chromedriver`](https://sites.google.com/a/chromium.org/chromedriver/)
  to be accessible from your `PATH`.
- `firefox` tends to break if you use the last version.
- `phantomjs` (default) is a safe choice but you won't see the interactions live.


