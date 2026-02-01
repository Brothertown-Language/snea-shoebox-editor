Docs: document Cloudflare Build settings token creation behavior

- Updated MANUAL_SETUP.md and SECURITY_ROTATION.md to reflect that the "Add a token" button in Cloudflare's Build settings UI may automatically create project-specific tokens (e.g., snea-backend-build, snea-frontend-build) with the correct permissions.
- This behavior is an acceptable alternative to manual token creation in the API Tokens profile settings.
- Clarified that these tokens can be used for both snea-backend and snea-editor projects.
