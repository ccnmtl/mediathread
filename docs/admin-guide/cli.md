# CLI & Management Commands

Mediathread is managed via the standard Django `manage.py` utility.

## Common Commands

Run these commands from the root of the project (or inside the Docker container).

### Database Management
*   `./manage.py migrate`: Applies database schema changes.
*   `./manage.py createsuperuser`: Creates an administrative account with full permissions.

### Static Files
*   `./manage.py collectstatic`: Gathers all static files (CSS, JS, Images) into the `static/` directory for production serving.

### User Management
*   `./manage.py change_password <username>`: Resets a user's password.

### Testing
*   `./manage.py test`: Runs the Python unit tests.
*   `make cypress`: Runs the Cypress end-to-end integration tests (requires Node.js).

## Custom Commands
(Check `manage.py help` for a full list of available commands, including any custom management commands added by installed apps.)
