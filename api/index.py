import os
import sys
from pathlib import Path

# Add project root and src/ directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
if str(BASE_DIR / "src") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "src"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

# Auto-apply database migrations on cold boot when using ephemeral /tmp database on Vercel
if os.getenv("VERCEL") == "1" and not os.getenv("DATABASE_URL"):
    try:
        from django.core.management import call_command
        call_command("migrate", interactive=False)
    except Exception as exc:
        print(f"Warning: Vercel auto-migrate failed: {exc}")

app = get_wsgi_application()
