# Development Status

## OPS-UDA-001 — UDA path-prefix compatibility
Status: IN PROGRESS

Flask Question now trusts one isolated UDA/Caddy forwarding hop to resolve URLs under `/apps/flask-question/`, while keeping direct LAN root access. Existing Flask form templates use `url_for`. Public UDA proxy access remains disabled; backend must not accept untrusted forwarded headers.

- [ ] CI passed and merged to main
- [ ] User tests forms, save and edit via UDA
