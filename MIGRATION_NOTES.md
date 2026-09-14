# Package Manager Migration: pip to UV

## Overview
Migrated `sectors` Django project from unmanaged `pip` with `requirements.txt` to `uv` using standard `pyproject.toml` and deterministic `uv.lock`.

## Changes Made
1. **Backups Created**: `requirements.txt.bak` (preserved; not deleted).
2. **Metadata Added**: `pyproject.toml` generated with PEP 621 metadata and explicit exact dependency constraints.
3. **Lockfile Created**: `uv.lock` generated with multi-platform resolution.
4. **Environment Initialized**: Isolated `.venv/` created and managed by `uv`.
5. **Ignore Rules**: `.venv/` and `*.bak` added to `.gitignore`.

## Command Replacement Table

| Task | Old Command (pip) | New Command (uv) |
|---|---|---|
| Create virtualenv | `python -m venv .venv` | `uv venv` |
| Install dependencies | `pip install -r requirements.txt` | `uv sync` |
| Add new package | `pip install <pkg> && pip freeze` | `uv add <pkg>` |
| Remove package | `pip uninstall <pkg>` | `uv remove <pkg>` |
| Run Django management | `python manage.py <cmd>` | `uv run python manage.py <cmd>` |
| Run test suite | `python manage.py test` | `uv run python manage.py test` |
| Run frontend build | `npm run build` | `npm run build` (unchanged) |
| List installed packages | `pip list` | `uv pip list` or `uv tree` |

## Common Troubleshooting

### 1. Hardlink warning on Windows (`UV_LINK_MODE`)
If you see:
```text
warning: Failed to hardlink files; falling back to full copy.
```
Set environment variable to silence it:
```powershell
$env:UV_LINK_MODE = "copy"
```

### 2. Running commands without activating venv
`uv run` automatically uses the virtualenv at `.venv` without requiring manual activation:
```powershell
uv run python manage.py runserver
```

### 3. Activating the virtualenv manually (if preferred)
```powershell
.venv\Scripts\Activate.ps1
```
