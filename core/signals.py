# core/signals.py
import os
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Manufacturer

@receiver(post_delete, sender=Manufacturer)
def delete_logo_file(sender, instance, **kwargs):
    """
    Remove the file from disk when a Manufacturer is deleted.
    """
    # If logo is a FieldFile, use its delete(); otherwise treat it as a path string
    logo_field = instance.logo
    try:
        logo_field.delete(save=False)
    except AttributeError:
        # assume it's a string path relative to MEDIA_ROOT
        file_path = os.path.join(settings.MEDIA_ROOT, logo_field)
        if os.path.exists(file_path):
            os.remove(file_path)
