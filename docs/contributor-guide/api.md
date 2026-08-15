# API Reference

Mediathread provides several API endpoints for interacting with data programmatically.

## Authentication
Most API endpoints require session authentication (cookie-based) or LTI context.

## Core Endpoints

### Assets
*   `GET /api/v2/assets/`: List available assets.
*   `POST /save/`: Endpoint for the Browser Extension to create new assets.

### Annotations
*   `GET /api/v2/annotations/`: Retrieve annotations for a specific asset.
*   `POST /api/v2/annotations/`: Create a new annotation.

*(Note: The API is currently primarily for internal use by the React frontend and is subject to change.)*
