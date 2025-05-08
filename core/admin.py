from django.contrib import admin

from .models import Manufacturer  # Make sure the import path is correct

admin.site.site_header = 'HeizungsDiscount24'
admin.site.site_title = 'Admin Panel'
admin.site.index_title = ''

admin.site.register(Manufacturer)
