# core/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('logo_management/', views.logo_management, name='logo_management'),
    path('shop_image_generation/', views.shop_image_generation, name='shop_image_generation'),
    path('sample_processing/', views.sample_processing, name='sample_processing'),
    path('upload-logo/', views.logo_uploaded, name='logo_uploaded'),
    path(
        "manufacturer/<int:pk>/delete/",
        views.manufacturer_delete,
        name="manufacturer_delete",
    ),
    path(
        "manufacturer/<int:pk>/edit/",
        views.manufacturer_edit,
        name="manufacturer_edit",
    ),
    path(
        "main_processing/",
        views.main_processing,
        name="main_processing",
    ),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
