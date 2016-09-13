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

preload_db: dataset metrics

clean:
	killall phantomjs || true
	rm -f ./tests/captures/*.png
	rm -rf -- ./datasets/chalearn/*/ # remove all folders

build:
	docker-compose up -d db
	docker-compose build

dev:
	docker-compose up -d db
	docker-compose run web python manage.py migrate
	docker-compose up web flower

superuser:
	@echo 'Run after `docker compose up`.'
	docker exec -t -i chalab_web_1 python manage.py createsuperuser

prod:
	docker-compose -f 'docker-compose.production.yml' up -d db
	docker-compose -f 'docker-compose.production.yml' build
	docker-compose -f 'docker-compose.production.yml' run --rm web python manage.py migrate
	docker-compose -f 'docker-compose.production.yml' up -d web static media flower

always:
	@ echo ""

NOW = $(shell date +%Y-%m-%d_%H%M%S)
CONTAINER_DB_SUFFIXED = chalab_db_volume_1_${NOW}

backupdb:
		docker commit -p chalab_db_volume_1 "${CONTAINER_DB_SUFFIXED}"
		docker save -o "./backups/${CONTAINER_DB_SUFFIXED}.tar" "${CONTAINER_DB_SUFFIXED}"
