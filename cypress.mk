cypress: $(JS_SENTINAL)
	npm run build
	npm run cypress:test

.PHONY: cypress
