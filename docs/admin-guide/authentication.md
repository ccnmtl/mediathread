# Authentication Configuration

Mediathread supports multiple authentication backends to suit different institutional needs.

## LTI (Learning Tools Interoperability)

This is the preferred method for integrating with Learning Management Systems (LMS) like Canvas, Blackboard, or Moodle.

### Configuration
1.  Ensure `lti_auth` is in `INSTALLED_APPS` (it is by default).
2.  The LTI launch endpoint is usually mapped in `lti_auth/urls.py`.
3.  You will need to configure the **Consumer Key** and **Shared Secret** in the Mediathread Admin interface (`/admin`).
    *   Go to **LTI Tool** > **LTI Consumers**.
    *   Add a new Consumer with the key/secret provided to your LMS administrator.

### Behavior
When a user launches Mediathread from an LMS:
*   **Account Creation:** If the user doesn't exist, an account is auto-created based on the LTI data.
*   **Role Mapping:** LTI roles (Instructor, Learner) are mapped to Mediathread Course roles (Faculty, Student).
*   **Course Context:** The user is automatically placed into the correct Course context.

## CAS (Central Authentication Service)

For university-wide Single Sign-On (SSO).

### Configuration
1.  Install `django-cas-ng`.
2.  Add to `AUTHENTICATION_BACKENDS` in your settings:
    ```python
    AUTHENTICATION_BACKENDS = (
        'django.contrib.auth.backends.ModelBackend',
        'django_cas_ng.backends.CASBackend',
    )
    ```
3.  Configure `CAS_SERVER_URL` in `local_settings.py`.

## Local Accounts

Mediathread uses `django-registration-redux` for local email/password accounts. This is useful for guest users or testing.
*   Users can sign up via the registration form (if enabled).
*   Admins can create accounts manually via `manage.py` or the Admin site.
