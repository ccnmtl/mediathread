===========================================================
Mediathread
===========================================================

[![Build Status](https://travis-ci.org/ccnmtl/mediathread.png)](https://travis-ci.org/ccnmtl/mediathread)

Mediathread is a Django application for multimedia annotations facilitating
group collaboration on video and image analysis. Developed at the Columbia
Center for New Media Teaching and Learning (CCNMTL)

CODE: http://github.com/ccnmtl/mediathread (see wiki for some dev documentation)  
INFO: http://ccnmtl.columbia.edu/mediathread  
FORUM: http://groups.google.com/group/mediathread

* [SherdJS](http://github.com/ccnmtl/SherdJS) 
* [django_courseaffils](http://github.com/ccnmtl/django_courseaffils) is our 'group space' Django app, which handles authorization from our university Single-Sign-On system.  This allows someone to select a course at the beginning and the user's environment is in that Course for the rest of the session.  If they are only in one course, then it automatically decorates the Django Request object with this course.


REQUIREMENTS
------------
Python 2.6 (or 2.5)  
Postgres (or MySQL)  

In Ubuntu (for postgres 8.4, but just change version numbers):

    $ sudo aptitude install postgres-8.4 postgresql-client-8.4 postgresql-server-dev-8.4 python-psycopg2 gcc python2.6 python-dev libc6-dev 


INSTALLATION
------------

1. Mediathread consists of the main application and the the SherdJS submodule. The SherdJS module
   contains all the javascript annotating code and media display viewers. This code was separated so that 
   it can be used on other non-Django platforms)
   
   To checkout:

       <code>git clone --recursive https://github.com/ccnmtl/mediathread.git</code>
    
2. Django settings  
   settings_shared.py contains common settings information  
   settings_stage.py/settings_production.py contain common overrides for test & production environments.  
   
   For local setup & sensitive information:  

    At CCNMTL, we use an unchecked-in local_settings.py file to hardwire very specific or very sensitive environment details, like database username and password
    or developer debug configuration. local_settings.py is automatically imported via the default Django settings.py file
    for the environment.
     
   For settings specific to your overall organization:  

    Mediathread also respects deploy_specific.settings.py, where we add custom settings 
    for our deployment that will not be included in the open-sourced distribution
    These settings are chiefly organization specific, like a Flickr api key and 
    instructions on where to route application errors and user problem reports.
     
     To create:

         $ mkdir deploy_specific
         $ touch deploy_specific/__init__.py
         $ touch deploy_specific/settings.py

         # override `settings_shared.py` values in the new settings.py file.

     See sample_deploy_specific_settings.py in /docs for more information   

2. Build the database  
   For Postgres:  

     A. Create the database `createdb mediathread`

   For MySQL:  
   
     A. Edit the file `requirements/libs.txt`
        - comment out the line `psycopg2`
        - uncomment `MySQLdb`
     B. Create the database

    <code>echo "CREATE DATABASE mediathread" | mysql -uroot -p mysql</code>

   To configure database settings:  
     Edit the DATABASES dictionary in your local_settings.py to point to your environment-specific location.  
     See here for Django doc on the DATABASES definition - https://docs.djangoproject.com/en/dev/ref/settings/#databases

3. Bootstrap uses virtualenv to build a contained library in `ve/`

    <code>./bootstrap.py</code>  
    
    NOTE: if you're using python2.5 use ./bootstrap-python25.py instead

 The rest of the instructions work like standard Django.  See:  
    http://docs.djangoproject.com/en/1.3/ for more details.

4. Sync the database

    <code>./manage.py syncdb
    ./manage.py migrate # to complete the south migration setup</code>
    
    If you are upgrading from a pre-south version of Mediathread
    (prior to May 29, 2012), please complete the following steps:
    * Perform a <code>./manage.py syncdb</code>
    * Run "Fakes" for each application
    <code>./manage.py migrate assetmgr 0001 --fake  
    ./manage.py migrate djangosherd 0001 --fake  
    ./manage.py migrate mediathread_main 0001 --fake  
    ./manage.py migrate projects 0001 --fake  
    ./manage.py migrate structuredcollaboration 0001 --fake  </code>

5. Run locally (during development ONLY)
    
    <code>./manage.py runserver myhost.example.com:8000</code>

6. For deployment to Apache, see our sample configuration in `apache/prod.conf`
   This directory also contains standard `django.wsgi` file which can be used
   with other webservers

INITIALIZATION
--------------

Go to your site in a web browser.

1. The default database is not very useful. Login with the superuser you
   created in Step #4.

2. Click the 'Create a Course' link.
    - Click the "+" to make a group.  Name it something like "test_course"
    - Click the "+" to make a faculty group.  Name it something like "test_course_faculty"
        - In the "Add users to group" field...
            - add yourself as a faculty member by putting your username with a "*" in front
              like this "*admin"
            - add some fellow faculty/student accounts -- you can create new accounts right here
              (read the instructions under the textarea)
        - Click "Save" and then click the upper-right link "Django administration" to get back to the regular site (yeah, not the most intuitive).
    - NOTE: If you have developer resources, you can make this process more integrated with your institution.  The developer would:
        - Make a comparable file to http://github.com/ccnmtl/django_courseaffils/blob/master/courseaffils/columbia.py
        - In your deploy_specific/settings.py, set COURSEAFFILS_COURSESTRING_MAPPER equal to the CourseStringMapper from that file        

3. Experiment with saving assets by visiting:

    http://myhost.example.com:8000/save/
   
    OR
   
    Install the bookmarklet from the homescreen and follow instructions there.

