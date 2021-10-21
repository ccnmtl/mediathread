# VERSION=1.8.0

# CHANGES:
# 1.9.0              - Use coverage tool directly to generate coverage
#                      reports.
#                    - wheel and pip updates
#                    - Use pre-compiled binary wheel for cryptography
# 1.8.0 - 2019-10-21 - Don't run flake8 on local_settings.py
# 1.7.0 - 2018-05-31 - Now using python 3 by default
#                    - Removed virtualenv.py in favor of python 3's
#                      builtin venv capability.
# 1.6.0 - 2017-09-05 - add bandit secure analysis configuration
# 1.5.0 - 2017-08-24 - remove jshint/jscs in favor of eslint
# 1.4.0 - 2017-06-06 - backout the switch to eslint. that's not really ready yet.
# 1.3.0 - 2017-06-05 - pypi location is not needed anymore
# 1.2.0 - 2016-12-15 - bump wheel version to 0.29
# 1.1.0 - 2016-11-08 - run flake8 tests before unit tests
# 1.0.1 - 2016-05-02 - Remove deprecated syncdb command from make install

VE ?= ./ve
MANAGE ?= ./manage.py
REQUIREMENTS ?= requirements.txt
SYS_PYTHON ?= python3
PY_SENTINAL ?= $(VE)/sentinal
WHEEL_VERSION ?= 0.36.2
PIP_VERSION ?= 21.2.4
MAX_COMPLEXITY ?= 10
INTERFACE ?= localhost
RUNSERVER_PORT ?= 8000
PY_DIRS ?= $(APP)

# Travis has issues here. See:
# https://github.com/travis-ci/travis-ci/issues/9524
ifeq ($(TRAVIS),true)
	BANDIT ?= bandit
	FLAKE8 ?= flake8
	PIP ?= pip
	COVERAGE ?= coverage
else
	BANDIT ?= $(VE)/bin/bandit
	FLAKE8 ?= $(VE)/bin/flake8
	PIP ?= $(VE)/bin/pip
	COVERAGE ?= $(VE)/bin/coverage
endif

jenkins: check flake8 test eslint jstest bandit

$(PY_SENTINAL): $(REQUIREMENTS)
	rm -rf $(VE)
	$(SYS_PYTHON) -m venv $(VE)
	$(PIP) install pip==$(PIP_VERSION)
	$(PIP) install --upgrade setuptools
	$(PIP) install wheel==$(WHEEL_VERSION)
	$(PIP) install --no-deps --requirement $(REQUIREMENTS)
	touch $@

test: $(PY_SENTINAL)
	$(COVERAGE) run --source='.' --omit=$(VE)/* $(MANAGE) test $(APP)
	$(COVERAGE) xml -o reports/coverage.xml

parallel-tests: $(PY_SENTINAL)
	$(MANAGE) test --parallel

bandit: $(PY_SENTINAL)
	$(BANDIT) --ini ./.bandit -r $(PY_DIRS)

flake8: $(PY_SENTINAL)
	$(FLAKE8) $(PY_DIRS) --max-complexity=$(MAX_COMPLEXITY) --exclude=*/local_settings.py,*/migrations/*.py --extend-ignore=$(FLAKE8_IGNORE)

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
