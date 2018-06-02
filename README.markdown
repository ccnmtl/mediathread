# Mediathread

[![Build Status](https://travis-ci.org/ccnmtl/mediathread.svg?branch=master)](https://travis-ci.org/ccnmtl/mediathread)
[![Documentation Status](https://readthedocs.org/projects/mediathread/badge/?version=latest)](https://mediathread.readthedocs.io/en/latest/?badge=latest) [![Greenkeeper badge](https://badges.greenkeeper.io/ccnmtl/mediathread.svg)](https://greenkeeper.io/)

Mediathread is a Django site for multimedia annotations facilitating
collaboration on video and image analysis. Developed at the Columbia
Center for New Media Teaching and Learning (CCNMTL)

CODE: http://github.com/ccnmtl/mediathread  
INFO: http://mediathread.info  
FORUM: http://groups.google.com/group/mediathread   

REQUIREMENTS
------------
Python 2.7
Postgres (or MySQL)  
Flowplayer installation for your site (See below for detailed instructions)  
Flickr API Key if you want to bookmark from FLICKR    


INSTALLATION
------------

1. Clone Mediathread

    git clone https://github.com/ccnmtl/mediathread.git

2. Build the database  
   For Postgres (preferred):  
     A. Create the database `createdb mediathread`  
  
   For MySQL: (Note: Mediathread is not well-tested on recent version of MySQL.)  
     A. Edit the file `requirements.txt`  
        - comment out the line `psycopg2`  
        - uncomment the `MySQL-python` line.

     B. Create the database  
  
    echo "CREATE DATABASE mediathread" | mysql -uroot -p mysql  
  
3. Customize settings  
    Create a local_settings.py file in the mediathread subdirectory. Override the variables from `settings_shared.py` that you need to customize for your local installation. At a minimum, you will need to customize your `DATABASES` dictionary.
     
     For more extensive customization and template overrides, you can create a deploy_specific directory to house a site-specific settings.py file:

         $ mkdir deploy_specific
         $ touch deploy_specific/__init__.py
         $ touch deploy_specific/settings.py

    Edit the `deploy_specific/settings.py` and override values in `settings_shared.py` like the `DATABASES` dictionary.
    This is where we add custom settings and templates for our deployment that will not be included in the open-sourced distribution.

4. Build the virtual environment
   Bootstrap uses virtualenv to build a contained library in `ve/`. `django.mk` specifies the build target for creating the virtualenv, and running any of the targets specified in that file will automatically set this up.

    make check

The rest of the instructions work like standard Django.  See: https://docs.djangoproject.com/ for more details.

5. Sync the database

    ./manage.py migrate

6. Run locally (during development only)
    ./manage.py runserver myhost.example.com:8000

Go to your site in a web browser.

7. The default database is not very useful. You'll need to create a course and some users. Login with the superuser you
   created in Step #5.

8. Click the 'Create a Course' link.
    - Click the "+" to make a group.  Name it something like "test_course"
    - Click the "+" to make a faculty group.  Name it something like "test_course_faculty"
        - In the "Add users to group" field...
            - add yourself as a faculty member by putting your username with a "*" in front
              like this "*admin"
            - add some fellow faculty/student accounts -- you can create new accounts right here
              (read the instructions under the textarea)
        - Click "Save" and then click the upper-right link "Django administration" to get back to the regular site (yeah, not the most intuitive).

9. Experiment with saving assets by visiting:
   http://myhost.example.com:8000/save/


DOCKER DEVELOPMENT
------------------

[Please note that the docker setup for Mediathread is still
experimental. There are likely to be rough edges here.]

If you have docker set up and docker-compose installed, you can get a
development environment up and running very quickly. To initialize it,
the following steps are recommended:

    $ make build
    $ docker-compose run web migrate
    $ docker-compose run web manage createsuperuser

After that, a simple:

    $ docker-compose up

will bring up a development server on port 8000 (if you are running
boot2docker, it may end up on a different port) backed by a PostgreSQL
database.

If requirements have been updated, you can rebuild the image by
re-running `make build`. Eventually, we'll be automatically publishing
the Mediathread Docker image to the Docker Hub and you will instead
be able to just run `docker pull ccnmtl/mediathread` to update.

The usual Django `manage.py` commands can be run inside the docker
compose container like so:

    $ docker-compose run web manage help
    $ docker-compose run web manage shell

(Note that it's with `manage`, not `manage.py`; this is the custom
entrypoint script (`docker-run.sh`) at work.)

You can run the unit tests inside the container with the following
command:

    $ docker-compose run web manage test --settings=mediathread.settings

That one's a *little* tricky and unintuitive. Normally, running
Mediathread inside the container via docker compose, it will use the
`settings_compose.py` settings file, which contains the configuration
for connecting to the PostgreSQL instance running in the other
container. For unit tests, you don't want that though, so the command
above explicitly sets it back to the default dev settings.

Production deployment with Docker is also possible, though even less
tested than development. The `settings_docker.py` file has the default
settings that the docker image uses and is designed to allow you to
override/set the important values through environment variables (so
configuration can be kept out of the docker image).

DJANGO SITE INFRASTRUCTURE
----------------
Mediathread makes use of the Django Sites framework. https://docs.djangoproject.com/en/1.6/ref/contrib/sites/

By default, Django creates a site called "example.com" with an id of 1. This id is referenced in settings_shared.py as SITE_ID=1.

In your production environment, RENAME example.com to your domain.

If a new site is created, update SITE_ID=<new site id> in your deploy_specific/settings.py or local_settings.py

ALLOWED_HOSTS
----------------

ALLOWED_HOSTS is "a list of strings representing the host/domain names that this Django site can serve. This is a security measure to prevent an attacker from poisoning caches and password reset emails with links to malicious hosts by submitting requests with a fake HTTP Host header, which is possible even under many seemingly-safe web server configurations." More here: https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts

Make sure the ALLOWED_HOSTS is set properly in your deploy_specific/settings.py or local_settings.py  


APACHE
----------------
For deployment to Apache, see our sample configuration in `apache/sample.conf`. This directory also contains standard `django.wsgi` file which can be used with other webservers

SSL
----------------
To support bookmarking assets from a variety of external sites, Mediathread instances must be accessible via http:// and https://


FLOWPLAYER
----------------
Mediathread instantiates a Flowplayer .swf or HTML5 player to play many video flavors.
Flowplayer requires you to have a local installation and will not
allow you to serve the player off their site. Free versions exist for both players.
Here are the basic instructions to install Flowplayer on your systems and point Mediathread at it.

1. Both versions are available here. https://flowplayer.org/pricing/#downloads. 
2. Install both versions on a public server on your site.
3. In the same directory as the Flash player, also install:  
    http://flash.flowplayer.org/plugins/streaming/rtmp.html - flowplayer.rtmp-3.2.13.swf  
    http://flash.flowplayer.org/plugins/streaming/pseudostreaming.html - flowplayer.pseudostreaming-3.2.13.swf  
    http://flash.flowplayer.org/plugins/streaming/audio.html - flowplayer.audio-3.2.11.swf  
    
4. In your local_settings.py or (better) deploy_specific/settings.py set FLOWPLAYER_SWF_LOCATION, like so:  
FLOWPLAYER_SWF_LOCATION= 'http://servername/directory/flowplayer-3.2.15.swf'
FLOWPLAYER_HTML5_LOCATION = 'http://<servername>/flowplayer-5.5.0/flowplayer.min.js'  
FLOWPLAYER_AUDIO_PLUGIN = 'flowplayer.audio-3.2.10.swf'  
FLOWPLAYER_PSEUDOSTREAMING_PLUGIN = 'flowplayer.pseudostreaming-3.2.11.swf'  
FLOWPLAYER_RTMP_PLUGIN = 'flowplayer.rtmp-3.2.11.swf'  

* For Flash, the plugins are picked up automatically from the same directory, so don't need the full path.  
* These are the versions we are currently using in production here at CU.

FLICKR
----------------
In your local_settings.py or (better) deploy_specific/settings.py specify your Flickr api key.  
DJANGOSHERD_FLICKR_APIKEY='your key here'

FLATPAGES
----------------
Mediathread's About & Help pages are constructed using the Django Flat Pages architecture. (https://docs.djangoproject.com/en/1.6/ref/contrib/flatpages/). In order to setup pages for your site, follow these steps:

1. Navigate to the Mediathread /admin/ area, Flatpages.

2. Create a new flat page, e.g. url: /help/ or /about/, select your domain site site and add content.

3. Save.

4. The page should be immediately available by navigating to yourdomain/help/ or yourdomain/about/


HELP DOCUMENTATION
----------------
Our help documentation tailored for the Columbia community and our in-house video upload system is here: http://support.ccnmtl.columbia.edu/knowledgebase/topics/6593. 

And, Nate Autune helpfully added this a few months ago, "Thanks to Rebecca Darling from Wellesley College, who graciously gave
permission to re-publish her "Mediathread Guide for Students" under a
Creative Commons license. Here is a link to where you can download it:
http://bit.ly/MediathreadStudentsGuide"


METADATA SUPPORT
----------------
1. Current development on the Mediathread browser extension is aimed at supporting the standard set forth by Schema.org (http://schema.org/). This format includes a system of hierarchal terms and their associated values. Use of the metadata terms itemscope, itemtype, and itemprop are used to help stucture the data such that Mediathread can make sense of what metadata is assocaited to the item or items being brought into the application. Examples of this structure can be found here: http://schema.org/docs/gs.html#microdata_itemscope_itemtype.

2. Use the Google Rich Snippet test tool to test your structure: http://www.google.com/webmasters/tools/richsnippets

3. It is also worth noting that the LRMI (Learning Resource Metadata Initiative) has been working with Schema.org in creating a more robust set of property (itemprop) terms that have been accepted into the standard. Some of these terms may be useful in determining what might best describe a data set or collection. Here is a link to this new specification: http://www.lrmi.net/the-specification
