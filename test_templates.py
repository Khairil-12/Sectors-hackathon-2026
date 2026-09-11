import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'sectors_copilot.settings'
import django
django.setup()
from django.template import engines
template_engine = engines['django']
print('Template DIRS:', template_engine.dirs)