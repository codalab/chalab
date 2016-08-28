test:
	DJANGO_SETTINGS_MODULE='instances.local' pytest

static: always
	DJANGO_SETTINGS_MODULE='instances.local' python manage.py collectstatic --noinput

migrations:
	DJANGO_SETTINGS_MODULE='instances.local' python manage.py makemigrations

dataset:
	cd ./datasets/chalearn/ && ./download.sh
	docker-compose run web python manage.py load_chalearn_dataset

metrics:
	docker-compose run web python manage.py load_default_metrics

dev:
	docker-compose build
	docker-compose up -d db
	docker-compose run web python manage.py migrate
	docker-compose up web

superuser:
	@echo "Run with docker compose up complete."
	docker exec -t -i chalab_web_1 python manage.py createsuperuser

prod:
	docker-compose -f 'docker-compose.production.yml' build
	docker-compose -f 'docker-compose.production.yml' up -d db
	docker-compose -f 'docker-compose.production.yml' run --rm web python manage.py migrate
	docker-compose -f 'docker-compose.production.yml' up -d web static

always:
	@ echo ""
