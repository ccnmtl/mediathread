# VERSION=1.2.0

# CHANGES:
# 1.2.0 - restore jshint/jscs

# expect JS_FILES to be set from the main Makefile, but default
# to everything in media/js otherwise.
JS_FILES ?= media/js

NODE_MODULES ?= ./node_modules
JS_SENTINAL ?= $(NODE_MODULES)/sentinal
JSHINT ?= $(NODE_MODULES)/jshint/bin/jshint
JSCS ?= $(NODE_MODULES)/jscs/bin/jscs
ESLINT ?= $(NODE_MODULES)/.bin/eslint

$(JS_SENTINAL): package.json
	rm -rf $(NODE_MODULES)
	npm install
	touch $(JS_SENTINAL)

jshint: $(JS_SENTINAL)
	$(JSHINT) $(JS_FILES)

jscs: $(JS_SENTINAL)
	$(JSCS) $(JS_FILES)

eslint: $(JS_SENTINAL)
	$(ESLINT) $(JS_FILES)

jstest: $(JS_SENTINAL)
	npm test

.PHONY: jshint jscs eslint jstest
