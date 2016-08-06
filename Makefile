test:
	DJANGO_SETTINGS_MODULE='instances.local' python manage.py test

dev:
	docker-compose build
	docker-compose run web python manage.py migrate
	docker-compose up web

prod:
	docker-compose -f 'docker-compose.production.yml' build
	docker-compose -f 'docker-compose.production.yml' run web python manage.py migrate
	docker-compose -f 'docker-compose.production.yml' up web -d

