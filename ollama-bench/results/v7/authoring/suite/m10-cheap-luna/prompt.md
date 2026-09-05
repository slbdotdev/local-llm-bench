# Preserve the catalog files' bytes

Update the catalog's two operator-facing values:

- In `config/formatting.ini`, change the `welcome` value to `Olá, catálogo — listo`.
- In `docs/operator_notes.txt`, change the `note` value to `Revisión completa`.

These files intentionally use CRLF line endings and UTF-8 non-ASCII text. Preserve both while
editing; do not rewrite them as LF or as another encoding, and do not normalize unrelated files.
The other settings and notes must remain unchanged.
