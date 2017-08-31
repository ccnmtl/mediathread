APP=mediathread
#JS_FILES=media/js/app media/js/lib/sherdjs/src media/js/lib/sherdjs/lib/tinymce/plugins/citation media/js/lib/sherdjs/lib/tinymce/plugins/editorwindow media/js/lib/sherdjs/src/configs
# sherdjs isn't jscs clean yet so for now:
JS_FILES=media/js/app
MAX_COMPLEXITY=7
PY_DIRS=$(APP) lti_auth structuredcollaboration terrain.py

all: jenkins

include *.mk

harvest1: $(PY_SENTINAL)
	$(MANAGE) harvest --settings=$(APP).settings_test --failfast -v 3 -a mediathread.main,mediathread.assetmgr,mediathread.taxonomy,mediathread.discussions

harvest2: $(PY_SENTINAL)
	$(MANAGE) harvest --settings=$(APP).settings_test --failfast -v 3 -a mediathread.projects

