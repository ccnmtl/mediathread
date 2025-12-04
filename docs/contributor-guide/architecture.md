# Architecture Overview

Mediathread is a hybrid application combining a robust Django backend with a modern React frontend.

## Backend (Django)

The backend is structured into several reusable Django apps located in `mediathread/`.

*   **`mediathread.main`**: Core functionality, home views, and shared utilities.
*   **`mediathread.projects`**: Manages "Projects" (collections of assets).
*   **`mediathread.assetmgr`**: Handles asset upload, storage, and metadata.
*   **`mediathread.taxonomy`**: Manages tagging vocabularies.
*   **`lti_auth`**: Handles LTI authentication logic.

### API Layer
Mediathread exposes data via two API frameworks:
1.  **Django Tastypie:** Used for older legacy APIs (Courses, Taxonomy).
2.  **Django REST Framework / Custom JSON Views:** Used for newer features and the React frontend.

## Frontend (React & Webpack)

The interactive parts of the application (specifically the Asset Analysis and Annotation interfaces) are built with React.

*   **Entry Points:** Defined in `webpack.config.js`.
*   **State Management:** React components manage local state for annotations and selections.
*   **Build System:** Webpack compiles ES6+ JavaScript and JSX into bundles served by Django.

## Database Schema
The application relies on **PostgreSQL**. Key models include:
*   `Course`: The central organizational unit.
*   `Asset`: Represents a media file (video/image).
*   `AssetSelection`: A specific time-range or crop of an Asset.
*   `Composition`: A user-created document embedding AssetSelections.
