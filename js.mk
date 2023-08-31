# VERSION=1.3.1

# CHANGES:
# 1.3.1 - conditionally install npm deps based on ENVIRONMENT var
# 1.3.0 - restore eslint
# 1.2.0 - restore jshint/jscs

# expect JS_FILES to be set from the main Makefile, but default
# to everything in media/js otherwise.
#
# When setting a custom value for this variable in your own Makefile,
# the line should look like this:
#   JS_FILES=media/js/src media/js/tests
#
# and not:
#   JS_FILES="media/js/src media/js/tests"
#
# Using quotes here will cause eslint to ignore this argument.
#
JS_FILES ?= media/js

NODE_MODULES ?= ./node_modules
JS_SENTINAL ?= $(NODE_MODULES)/sentinal
ESLINT ?= $(NODE_MODULES)/.bin/eslint

NPM_OPTS = --include=dev

ifeq ($(ENVIRONMENT),production)
	NPM_OPTS = --only=prod
endif
ifeq ($(ENVIRONMENT),staging)
	NPM_OPTS = --only=prod
endif

$(JS_SENTINAL): package.json
	rm -rf $(NODE_MODULES)
	npm install $(NPM_OPTS)
	touch $(JS_SENTINAL)

eslint: $(JS_SENTINAL)
	$(ESLINT) $(JS_FILES)

jstest: $(JS_SENTINAL)
	npm test

.PHONY: eslint jstest
