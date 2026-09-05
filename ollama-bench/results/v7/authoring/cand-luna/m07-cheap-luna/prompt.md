# Rename the watermark factory

Rename the public factory for the watermark stage from `build_watermark` to `load_watermark`.
Update every ordinary code, documentation, test, and configuration reference so the old public
name is no longer used anywhere in the repository. The factory's behavior and all other stage
APIs must remain unchanged. Do not add a compatibility alias.
