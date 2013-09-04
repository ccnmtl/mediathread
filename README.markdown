===========================================================
Mediathread
===========================================================

[![Build Status](https://travis-ci.org/ccnmtl/mediathread.png)](https://travis-ci.org/ccnmtl/mediathread)

Mediathread is a Django site for multimedia annotations facilitating
collaboration on video and image analysis. Developed at the Columbia
Center for New Media Teaching and Learning (CCNMTL)

CODE: http://github.com/ccnmtl/mediathread (see wiki for some dev documentation)
INFO: http://ccnmtl.columbia.edu/mediathread
FORUM: http://groups.google.com/group/mediathread

REQUIREMENTS
------------
Python 2.7 (Python 2.6 is still supported, but we encourage you to upgrade.)
Postgres (or MySQL)
Flowplayer installation for your site (See below for detailed instructions)


INSTALLATION
------------

1. Clone Mediathread

    git clone https://github.com/ccnmtl/mediathread.git

2. Build the database
   For Postgres:
     A. Create the database `createdb mediathread`

   For MySQL:
     A. Edit the file `requirements/libs.txt`
        - comment out the line `psycopg2`
        - uncomment `MySQLdb`
     B. Create the database

    echo "CREATE DATABASE mediathread" | mysql -uroot -p mysql

   For Both:
     Edit the variables in `settings_shared.py` that you need to customize for your local installation.
     At a minimum, you will need to customize your `DATABASES` dictionary as appropriate.
     
     For more extensive customization, you can create a deploy_specific directory to house a site-specific settings.py file:

         $ mkdir deploy_specific
         $ touch deploy_specific/__init__.py

       # edit a file called `deploy_specific/settings.py` setting those same variables
         which will override the values in `settings_shared.py`
         This is where we add custom settings for our deployment that will not
         be included in the open-sourced distribution


3. Bootstrap uses virtualenv to build a contained library in `ve/`

    ./bootstrap.py

The rest of the instructions work like standard Django.  See:
 http://docs.djangoproject.com/en/1.1/ for more details.

4. Sync the database

    ./manage.py syncdb
    ./manage.py migrate # to complete the south migration setup

5. Run locally (during development only)
    ./manage.py runserver myhost.example.com:8000

6. For deployment to Apache, see our sample configuration in `apache/prod.conf`
   This directory also contains standard `django.wsgi` file which can be used
   with other webservers

Go to your site in a web browser.

7. The default database is not very useful.  Login with the superuser you
   created in Step #4.

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

10. For deployment, take a look at the `apache/` directory for sample apache configuration files

FLOWPLAYER
----------------
Mediathread instantiates a Flowplayer .swf to play many video flavors.
Flowplayer now requires you to have a local installation and will not
allow you to serve the player off their site. Here are the basic instructions
to install Flowplayer on your systems and point Mediathread at it.

1. http://flash.flowplayer.org/download/ # Version 3.2.15 or higher
2. Install on a public server on your site.
3. In the same directory, install:
    http://flash.flowplayer.org/plugins/streaming/rtmp.html - flowplayer.rtmp-3.2.12.swf
    http://flash.flowplayer.org/plugins/streaming/pseudostreaming.html - flowplayer.pseudostreaming-3.2.12.swf
    http://flash.flowplayer.org/plugins/streaming/audio.html - flowplayer.audio-3.2.10.swf
    
4. In your local_settings.py or (better) deploy_specific/settings.py set FLOWPLAYER_SWF_LOCATION, like so:
FLOWPLAYER_SWF_LOCATION=http://<servername>/<directory>/flowplayer-3.2.15.swf

The plugins are picked up automatically from the same directory.


METADATA SUPPORT
----------------
1. Current development on the Mediathread bookmarklet is aimed at supporting the standard set forth by Schema.org (http://schema.org/). This format includes a system of hierarchal terms and their associated values. Use of the metadata terms itemscope, itemtype, and itemprop are used to help stucture the data such that Mediathread can make sense of what metadata is assocaited to the item or items being brought into the application. Examples of this structure can be found here: http://schema.org/docs/gs.html#microdata_itemscope_itemtype.

2. Use the Google Rich Snippet test tool to test your structure: http://www.google.com/webmasters/tools/richsnippets

3. It is also worth noting that the LRMI (Learning Resource Metadata Initiative) has been working with Schema.org in creating a more robust set of property (itemprop) terms that have been accepted into the standard. Some of these terms may be useful in determining what might best describe a data set or collection. Here is a link to this new specification: http://www.lrmi.net/the-specification
