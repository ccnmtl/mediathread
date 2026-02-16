# See README  (https://github.com/ccnmtl/mediathread/blob/master/README.markdown)
# For more information on how to setup a deploy_specific directory

EXTRA_INSTALLED_APPS = (
    'mediathread.deploy_specific',
)

# Configure your database configuration for staging & production
{% if STAGING_ENV %}
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
{% else %}
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
{% endif %}

SERVER_EMAIL = '<your domain specific email>'
DEFAULT_FROM_EMAIL = SERVER_EMAIL  # Used by registration

ADMINS = (
    ('YOUR_GROUP', 'mediathread-sysadmin@example.edu'),
)

# custom authentication module
# AUTHENTICATION_BACKENDS.insert(0, 'custom.authentication.Backend')

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'

# get your own course string mapper that works with your group's
# custom authentication app (presumably auto-creating/auto-adding groups)
# from courseaffils.columbia import CourseStringMapper
# COURSEAFFILS_COURSESTRING_MAPPER = CourseStringMapper

# This variable is for DRMy URLs which will be generated on the fly
# when the asset is displayed.  See assetmgr/models.py
# arguments are (source, request)
# and the processed Source URL should be returned
# ASSET_URL_PROCESSOR = some_url_processor

# Support Flickr in the extension
# DJANGOSHERD_FLICKR_APIKEY = ''

# For LTI integration
PYLTI_CONFIG = {
    'consumers': {
        '<key>': {
            'secret': '<secret>'
        }
    }
}

LTI_ELEVATE_TEACHINGASSISTANTS = [
    '<www.canvas.site>'
]
