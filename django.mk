# VERSION=1.4.0

# CHANGES:
# 1.4.0 - 2017-06-06 - backout the switch to eslint. that's not really ready yet.
# 1.3.0 - 2017-06-05 - pypi location is not needed anymore
# 1.2.0 - 2016-12-15 - bump wheel version to 0.29
# 1.1.0 - 2016-11-08 - run flake8 tests before unit tests
# 1.0.1 - 2016-05-02 - Remove deprecated syncdb command from make install

VE ?= ./ve
MANAGE ?= ./manage.py
FLAKE8 ?= $(VE)/bin/flake8
REQUIREMENTS ?= requirements.txt
SYS_PYTHON ?= python
PIP ?= $(VE)/bin/pip
PY_SENTINAL ?= $(VE)/sentinal
WHEEL_VERSION ?= 0.29.0
VIRTUALENV ?= virtualenv.py
SUPPORT_DIR ?= requirements/virtualenv_support/
MAX_COMPLEXITY ?= 10
INTERFACE ?= localhost
RUNSERVER_PORT ?= 8000
PY_DIRS ?= $(APP)

jenkins: check flake8 test jshint jscs

$(PY_SENTINAL): $(REQUIREMENTS) $(VIRTUALENV) $(SUPPORT_DIR)*
	rm -rf $(VE)
	$(SYS_PYTHON) $(VIRTUALENV) --extra-search-dir=$(SUPPORT_DIR) --never-download $(VE)
	$(PIP) install wheel==$(WHEEL_VERSION)
	$(PIP) install --use-wheel --no-deps --requirement $(REQUIREMENTS)
	$(SYS_PYTHON) $(VIRTUALENV) --relocatable $(VE)
	touch $@

test: $(PY_SENTINAL)
	$(MANAGE) jenkins --pep8-exclude=migrations --enable-coverage --coverage-rcfile=.coveragerc

parallel-tests: $(PY_SENTINAL)
	$(MANAGE) test --parallel

flake8: $(PY_SENTINAL)
	$(FLAKE8) $(PY_DIRS) --max-complexity=$(MAX_COMPLEXITY)

runserver: check
	$(MANAGE) runserver $(INTERFACE):$(RUNSERVER_PORT)

migrate: check jenkins
	$(MANAGE) migrate

check: $(PY_SENTINAL)
	$(MANAGE) check

shell: $(PY_SENTINAL)
	$(MANAGE) shell_plus

clean:
	rm -rf $(VE)
	rm -rf media/CACHE
	rm -rf reports
	rm -f celerybeat-schedule
	rm -f .coverage
	rm -rf node_modules
	find . -name '*.pyc' -exec rm {} \;

pull:
	git pull
	make check
	make test
	make migrate
	make flake8

rebase:
	git pull --rebase
	make check
	make test
	make migrate
	make flake8

# run this one the very first time you check
# this out on a new machine to set up dev
# database, etc. You probably *DON'T* want
# to run it after that, though.
install: jenkins
	createdb $(APP)
	make migrate

.PHONY: jenkins test flake8 runserver migrate check shell clean pull rebase install
