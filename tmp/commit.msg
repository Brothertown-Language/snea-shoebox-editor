docs: fix Cloudflare Pages deployment command and configuration

- Added mandatory `--project-name snea-editor` to the frontend deploy command in `docs/deployment/MANUAL_SETUP.md`.
- Added `pages_build_output_dir = "."` to `wrangler.toml` to satisfy Cloudflare Pages configuration requirements.
- Updated documentation/ACTIVE_TASK.md with session progress.