APP=mediathread
#JS_FILES=media/js/app media/js/lib/sherdjs/src media/js/lib/sherdjs/lib/tinymce/plugins/citation media/js/lib/sherdjs/lib/tinymce/plugins/editorwindow media/js/lib/sherdjs/src/configs
# sherdjs isn't jscs clean yet so for now:
JS_FILES=media/js/app media/js/src cypress/**/*.js media/js/pdf/*.js
MAX_COMPLEXITY=9
PY_DIRS=$(APP) lti_auth structuredcollaboration
FLAKE8_IGNORE=W605

all: jenkins

include *.mk

jsbuild: $(JS_SENTINAL)
	npm run build

integrationserver: $(PY_SENTINAL)
	$(MANAGE) integrationserver
