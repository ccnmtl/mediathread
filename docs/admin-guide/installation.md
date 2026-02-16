# Installation & Deployment

Mediathread is a complex Django application dependent on several services. We recommend using Docker for development and evaluation, and a standard WSGI setup (Apache/Nginx) for production.

## Requirements
*   **Python:** >= 3.8
*   **Database:** PostgreSQL (Recommended)
*   **JavaScript:** Node.js & NPM (for building the frontend)
*   **Video Player:** Flowplayer installation (optional, for legacy support)
*   **External Services:** Flickr API Key (optional)

## Docker (Development)

The easiest way to spin up Mediathread is using Docker Compose.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ccnmtl/mediathread.git
    cd mediathread
    ```

2.  **Build the images:**
    ```bash
    make build
    ```

3.  **Initialize the database:**
    ```bash
    docker-compose run web migrate
    docker-compose run web manage createsuperuser
    ```

4.  **Run the application:**
    ```bash
    docker-compose up
    ```
    The site will be available at `http://localhost:8000`.

## Production Deployment

For production, we utilize standard Django deployment practices.

1.  **Virtual Environment:** Create a virtualenv and install dependencies from `requirements.txt`.
2.  **Static Files:** Run `./manage.py collectstatic` to gather CSS/JS assets.
3.  **WSGI Server:** Use Gunicorn or Apache with `mod_wsgi`. Sample Apache configs are in `apache/`.
4.  **Settings:** Create a `deploy_specific/settings.py` to override `settings_shared.py`.
    *   Set `DEBUG = False`
    *   Configure `DATABASES`
    *   Set `ALLOWED_HOSTS`
