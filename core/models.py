from django.db import models

# Create your models here.
class Manufacturer(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing ID (optional, Django adds this by default)
    name = models.CharField(max_length=500)
    logo = models.CharField(max_length=500)  # Path to logo as string
    date_created = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=True)  # 1 for active, 0 for inactive

    def __str__(self):
        return self.name
