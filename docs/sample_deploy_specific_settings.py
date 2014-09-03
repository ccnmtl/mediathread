# Put this file in deploy_specific/settings.py

# if you actually have template overrides or your own views, etc.
# EXTRA_INSTALLED_APPS = (
#    'mediathread.deploy_specific',
#    )

ADMINS = (
    ('YOUR_GROUP', 'mediathread-sysadmin@example.edu'),
)

# SERVER_EMAIL = "mediathread@example.com"
# PUBLIC_CONTACT_EMAIL = "mediathread@example.com"

# developer IPs
INTERNAL_IPS = ('000.000.000.000',)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mediathread',
        'HOST': 'localhost',
        'PORT': 5432,  # using standard PostgreSQL installation
        'USER': 'postgres',
        'PASSWORD': 'postgres',
    }
}

# custom authentication module
# AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'

# http://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = ''

# get your own course string mapper that works with your group's
# custom authentication app (presumably auto-creating/auto-adding groups)
# from courseaffils.columbia import CourseStringMapper
# COURSEAFFILS_COURSESTRING_MAPPER = CourseStringMapper

# This variable is for DRMy URLs which will be generated on the fly
# when the asset is displayed.  See assetmgr/models.py
# arguments are (source, request)
# and the processed Source URL should be returned
# ASSET_URL_PROCESSOR = some_url_processor

# These are used for supporting flickr in the bookmarklet and
# using flowplayer to show flash-supported video (h264,flv,rtmp)

# DJANGOSHERD_FLICKR_APIKEY = ''
# FLOWPLAYER_SWF_LOCATION = ""

# These variables are used for
# External url for issue reporting system or e-mail notification
# Accepts a post string with various bits of information collected
# from a Contact Us form.
# See templates/main/contact.html for specific form fields
# CONTACT_US_DESTINATION = ""
