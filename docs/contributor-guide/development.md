# Development Setup

We welcome contributions! Follow these steps to set up your environment.

## Prerequisites
*   Docker & Docker Compose (Recommended)
*   Node.js & NPM (for frontend changes)

## Getting Started

1.  **Fork & Clone:** Fork the repo on GitHub and clone it locally.
2.  **Build Environment:**
    ```bash
    make build
    ```
3.  **Run Tests:**
    Always run tests before submitting a PR.
    *   **Unit Tests:** `docker-compose run web manage test`
    *   **Integration Tests:** `make cypress`

## Code Style
*   **Python:** We follow PEP 8. Usage of linters (flake8) is encouraged.
*   **JavaScript:** We use ESLint. Run `npm run lint` to check your code.

## Making Changes
1.  Create a feature branch (`git checkout -b feature/my-new-feature`).
2.  Make your changes.
3.  Write tests covering your changes.
4.  Run the full test suite.
5.  Push to your fork and submit a Pull Request.
