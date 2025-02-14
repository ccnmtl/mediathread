The lti_auth django app contains all of Mediathread's LTI-related
code. There are two main things going on here:

* LTI 1.1 code using the [pylti](https://github.com/mitodl/pylti)
  library (this code was actually the foundation implementation for the
  [django-lti-provider](https://github.com/ccnmtl/django-lti-provider)
  library).
* LTI 1.3 using the
  [django-lti](https://github.com/academic-innovation/django-lti)/[pylti1p3](https://github.com/dmitry-viskov/pylti1.3)
  libraries.

Because LTI 1.1 is now deprecated, we have been working to get the new
LTI 1.3 configuration working.

Canvas allows LTI integration in a few different ways. Within a
course, you can select Settings, and then the Apps tab. From here, you
can add an LTI app using a number of different methods, i.e.: Manual
Entry, By URL, Paste XML, By Client ID, or By LTI 2 Registration URL.
Most of these methods actually refer to the deprecated LTI 1.1
protocol (keep in mind LTI 2 is also deprecated, and is actually older
than LTI 1.3). The most reliable method I've found here is to use "By
Client ID".

## Mediathread / Canvas integration (LTI 1.3)

To integrate Mediathread with Canvas, first we create an LTI
Registration in Mediathread's admin page:
* `https://<mediathread hostname>/admin/lti_tool/ltiregistration/`

1. Click "Add LTI Registration"
2. Name: Canvas instance hostname, e.g. `canvas.ctl.columbia.edu`
3. UUID: This is filled in automatically
4. Issuer: `https://<canvas instance hostname>`
5. Client ID: Set to 1 for now, this will be updated later
6. Auth URL: `https://<canvas instance hostname>/api/lti/authorize_redirect`
7. Access token URL: `https://<canvas instance hostname>/login/oauth2/auth`
8. Keyset URL: `https://<canvas instance hostname>/api/lti/security/jwks`

Then, in Canvas, navigate to Admin -> CTL -> Developer Keys.

1. Click the blue "+ Developer Key" button and select "LTI Key". ("API
   Key" here refers to Canvas's custom API which we don't have special
   integration for, so we definitely want to choose "LTI Key" here.)
2. Select Method -> Enter URL
3. Enter the URL: `https://<your mediathread hostname>/lti/<registration uuid>/config.json`
4. Fill in the Key Name as Mediathread, as well as an admin email for
   Owner Email.
5. Under Redirect URIs, add: `https://<your mediathread hostname>/lti/launch/`
6. Click Save
7. Under "Details", you will see an ID like "10000000000018". This is the "Client ID".
   Go back to the LTI Registration in Mediathread and update the Client ID with this
   value. Without doing this, the LTI launch will raise:
   `OIDCException: Could not find registration details`

Once the LTI Registration and the Developer Key are in place, you can
add this LTI App to a course.

1. Navigate to a course in Canvas, and go to Settings.
2. Click the Apps tab, and click the "+ App" button to add a new app.
3. Under Configuration Type, select "By Client ID".
4. For the Client ID, input the ID of the Developer Key you created, which
   should look something like "10000000000018".
5. Click Submit.

The Mediathread LTI app should now be installed in this course. You can
click on the gear icon, then Placements to see app placements. The
"Course Navigation" placement should be active, and this is adds a
"Mediathread" menu item in the course sidebar. Sometimes the Placements
aren't automatically configured on the first try. If you don't see the
Mediathread menu item on the left, go back to the Developer Key and see
how things are configured, and save this again if necessary. This should
be smoothed over once we migrate to the new "LTI Dynamic Registration",
which Canvas only recently added support for. See:
https://github.com/academic-innovation/django-lti/pull/135#issuecomment-2644062255

Now, there is still one more thing to do: the LTI Deployment must be made
"active". To do this:

1. Select the Mediathread menu item in the course. You should receive the
   error message "This deployment is not active". This is an expected error
   message that comes from django-lti.
2. Navigate to your LTI Registration management admin screen in Mediathread,
   and look under LTI Deployments. You should see one populated now, and
   simply select the "Is Active" checkbox, and Save.

Now, *finally*, the tool should successfully launch within Canvas.

## Notes about LTI libraries

Python support for LTI 1.3 is not in the most cohesive state right now, as
different people have contributed their efforts at different times and in
different places. That said, it has been possible to get things working
building off what open source libraries have been built.

[pylti1.3](https://github.com/dmitry-viskov/pylti1.3) is a good base to build
off of. And although it is not actively maintained, it is entirely possible to
override anything we need to, when necessary.

A lot of the functionality in pylti1.3 is pretty low-level though, and a lot
of the LTI transactions and setup can be pre-configured when working with
Django. Fortunately a lot of this work has been done by the
[django-lti](https://github.com/academic-innovation/django-lti) library, which
builds off of pylti1.3. There is some overlap in functionality here, as pylti1.3
also contains some Django-specific code. But the django-lti library fills in the
gaps, and is under active development and open to suggestions that we might find
helpful as we work deeper with LTI 1.3 integration.
