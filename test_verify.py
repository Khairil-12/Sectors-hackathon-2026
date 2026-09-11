import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'sectors_copilot.settings'

import django
django.setup()

from django.contrib.staticfiles import finders

# Find static files
static_files = ['dist/app.css', 'src/input.css']
for f in static_files:
    path = finders.find(f)
    status = 'found' if path else 'not found'
    print('Static %s: %s -> %s' % (f, status, path))

# Check templates
templates = ['base.html', 'components/app_shell.html', 'components/prompt_composer.html']
for t in templates:
    path = finders.find(t)
    status = 'found' if path else 'not found'
    print('Template %s: %s -> %s' % (t, status, path))