The lti_auth django app contains all of Mediathread's LTI-related
code. There are two main things going on here:

* LTI 1.1 code using the [pylti](https://github.com/mitodl/pylti)
  library (this code was actually the foundation implementation for the
  [django-lti-provider](https://github.com/ccnmtl/django-lti-provider)
  library).
* LTI 1.3 using the
  [django-lti](https://github.com/academic-innovation/django-lti)/[pylti1p3](https://github.com/dmitry-viskov/pylti1.3)
  libraries.

Because LTI 1.1 is now deprecated, though still functional, we have
been doing a focused effort to get the new LTI 1.3 configuration
working.

Canvas allows LTI integration in a few different ways. Within a
course, you can select Settings, and then the Apps tab. From here, you
can add an LTI app using a number of different methods, i.e.: Manual
Entry, By URL, Paste XML, By Client ID, or By LTI 2 Registration URL.
Most of these methods actually refer to the deprecated LTI 1.1
protocol (keep in mind LTI 2 is also deprecated, and is actually older
than LTI 1.3). The most reliable method I've found here is to use "By
Client ID".

In order to add an LTI app by client ID, you must first create a
Developer Key for this app. In Canvas, navigate to Admin -> CTL ->
Developer Keys.

1. Click the blue "+ Developer Key" button and select "LTI Key". ("API
   Key" here refers to Canvas's custom API which we don't have special
   integration for, so we definitely want to choose "LTI Key" here.)
2. Select Method -> Enter URL
3. Enter the URL: `https://<your mediathread hostname>/lti/config.json`
4. Fill in the Key Name as Mediathread, as well as an admin email for
   Owner Email.
5. Click Save