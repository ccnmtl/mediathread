# VERSION=2.0.0
# Docker related stuff

# Start up docker dev server with docker-compose
docker:
	docker compose up

# Enter a command-line shell in the web container
docker-shell:
	docker compose run web bash

# Enter an interactive django shell
docker-django-shell:
	docker compose run web python manage.py shell_plus \
		--settings=$(APP).settings_docker

.PHONY: docker docker-shell docker-django-shell
