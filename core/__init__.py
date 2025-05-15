import os
from django.conf import settings

os.makedirs(os.path.join(settings.MEDIA_ROOT, 'pdf_conversions'), exist_ok=True)
os.makedirs(os.path.join(settings.MEDIA_ROOT, 'pdf_conversion_logs'), exist_ok=True)