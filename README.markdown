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
Python 2.6 (or 2.5)
Postgres (or MySQL)

In Ubuntu (for postgres 8.4, but just change version numbers):

    $ sudo aptitude install postgres-8.4 postgresql-client-8.4 postgresql-server-dev-8.4 python-psycopg2 gcc python2.6 python-dev libc6-dev 


INSTALLATION
------------

1. Mediathread relies on several submodules.  The easiest way to download
   it all is to run with git 1.6.5+ is:

    git clone --recursive https://github.com/ccnmtl/mediathread.git

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
     At a minimum, you will need to custimze your the `DATABASES` dictionary as appropriate.

     If you are not running a statsd server, you should disable the 'django_statsd' application by removing 
     it from the INSTALLED_APPS list.
     
     Even better would be:

         $ mkdir deploy_specific
         $ touch deploy_specific/__init__.py

       # edit a file called `deploy_specific/settings.py` setting those same variables
         which will override the values in `settings_shared.py`
         This is where we add custom settings for our deployment that will not
         be included in the open-sourced distribution



3. Bootstrap uses virtualenv to build a contained library in `ve/`

    ./bootstrap.py
    NOTE: if you're using python2.5 use ./bootstrap-python25.py instead

The rest of the instructions work like standard Django.  See:
 http://docs.djangoproject.com/en/1.1/ for more details.

4. Sync the database

    ./manage.py syncdb
    ./manage.py migrate # to complete the south migration setup

5. Run locally (during development)
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
