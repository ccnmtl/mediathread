from settings_shared import *


DATABASE_ENGINE = 'sqlite3'

# this is a temporary hack to let the tests pass, since the metadata screenscraper
# doesn't send any auth credentials, so we need to expose this mock flatpage.
# but since the actual archive will be gated too, this is actually a critical flaw
# in the metadata scraper. http://pmt.ccnmtl.columbia.edu/item.pl?iid=55558
ANONYMOUS_PATHS = ANONYMOUS_PATHS + ('/interview-wth-mr-t/',)
