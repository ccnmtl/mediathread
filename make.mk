# VERSION=1.0.0

GITHUB_BASE ?= https://raw.githubusercontent.com/ccnmtl/makefiles/master/
WGET ?= wget
WGET_FLAGS ?= "-O"

update_makefiles:
	for f in $$(grep -l "^# VERSION=" *.mk) ; do \
		$(WGET) $(GITHUB_BASE)$$f $(WGET_FLAGS) $$f ; \
	done

.PHONY: update_makefiles
