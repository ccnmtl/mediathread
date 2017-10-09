# VERSION=1.3.0

# CHANGES:
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

$(JS_SENTINAL): package.json
	rm -rf $(NODE_MODULES)
	npm install
	touch $(JS_SENTINAL)

eslint: $(JS_SENTINAL)
	$(ESLINT) $(JS_FILES)

jstest: $(JS_SENTINAL)
	npm test

.PHONY: eslint jstest
