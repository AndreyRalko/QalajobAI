import os

env = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

if env == 'config.settings.prod':
    from .prod import *
else:
    from .dev import *

