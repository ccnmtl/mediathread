ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
MANAGE=./manage.py
APP=mediathread
FLAKE8=./ve/bin/flake8

ifeq ($(TAG), undefined)
	IMAGE = ccnmtl/$(APP)
else
	IMAGE = ccnmtl/$(APP):$(TAG)
endif

jenkins: ./ve/bin/python validate jshint jscs flake8 test

./ve/bin/python: requirements.txt bootstrap.py virtualenv.py
	./bootstrap.py

jshint: node_modules/jshint/bin/jshint
	./node_modules/jshint/bin/jshint --config=.jshintrc media/js/app/ media/js/lib/sherdjs/src

jscs: node_modules/jscs/bin/jscs
	./node_modules/jscs/bin/jscs media/js/app/

node_modules/jshint/bin/jshint:
	npm install jshint --prefix .

node_modules/jscs/bin/jscs:
	npm install jscs --prefix .

test: ./ve/bin/python
	$(MANAGE) jenkins --pep8-exclude=migrations --enable-coverage --coverage-rcfile=.coveragerc

harvest1: ./ve/bin/python
	$(MANAGE) harvest --settings=mediathread.settings_test --failfast -v 4 mediathread/main/features
	$(MANAGE) harvest --settings=mediathread.settings_test --failfast -v 4 mediathread/assetmgr/features
	$(MANAGE) harvest --settings=mediathread.settings_test --failfast -v 4 mediathread/taxonomy/features

harvest2: ./ve/bin/python
	$(MANAGE) harvest --settings=mediathread.settings_test --failfast -v 4 mediathread/projects/features

flake8: ./ve/bin/python
	$(FLAKE8) $(APP) --max-complexity=9
	$(FLAKE8) structuredcollaboration --max-complexity=8
	$(FLAKE8) lti_auth --max-complexity=8

runserver: ./ve/bin/python validate
	$(MANAGE) runserver

migrate: ./ve/bin/python validate jenkins
	$(MANAGE) migrate

validate: ./ve/bin/python
	$(MANAGE) validate

shell: ./ve/bin/python
	$(MANAGE) shell_plus

clean:
	rm -rf ve
	rm -rf media/CACHE
	rm -rf reports
	rm -f celerybeat-schedule
	rm -rf .coverage
	find . -name '*.pyc' -exec rm {} \;

pull:
	git pull
	make validate
	make test
	make migrate
	make flake8

rebase:
	git pull --rebase
	make validate
	make test
	make migrate
	make flake8

# run this one the very first time you validate
# this out on a new machine to set up dev
# database, etc. You probably *DON'T* want
# to run it after that, though.
install: ./ve/bin/python validate jenkins
	createdb $(APP)
	$(MANAGE) syncdb --noinput
	make migrate

wheelhouse/requirements.txt: requirements.txt
	mkdir -p wheelhouse
	docker run --rm \
	-v $(ROOT_DIR):/app \
	-v $(ROOT_DIR)/wheelhouse:/wheelhouse \
	ccnmtl/django.build
	cp requirements.txt wheelhouse/requirements.txt
	touch wheelhouse/requirements.txt

build: wheelhouse/requirements.txt
	docker build -t $(IMAGE) .
