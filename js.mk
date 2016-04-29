# VERSION=1.0.0
# expect JS_FILES to be set from the main Makefile, but default
# to everything in media/js otherwise.
JS_FILES ?= media/js

NODE_MODULES ?= ./node_modules
JS_SENTINAL ?= $(NODE_MODULES)/sentinal
JSHINT ?= $(NODE_MODULES)/jshint/bin/jshint
JSCS ?= $(NODE_MODULES)/jscs/bin/jscs

$(JS_SENTINAL): package.json
	rm -rf $(NODE_MODULES)
	npm install
	touch $(JS_SENTINAL)

jshint: $(JS_SENTINAL)
	$(JSHINT) $(JS_FILES)

jscs: $(JS_SENTINAL)
	$(JSCS) $(JS_FILES)

jstest: $(JS_SENTINAL)
	npm test

.PHONY: jshint jscs jstest
