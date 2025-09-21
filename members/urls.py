from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Auth
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("auth/", views.auth_tabs, name="auth_tabs"),

    # Members
    path("members/", views.members, name="members"),
    path("members/<int:id>/", views.details, name="details"),
    path("members/<int:id>/edit/", views.edit_profile, name="edit_profile"),

    # Intro (chung cho tất cả)
# Intro (chung cho tất cả, không cần id)
    path("intro/", views.template_intro, name="template_intro"),

    # Product (theo từng user)
    path("members/<int:id>/products/", views.template_product, name="template_product"),
    path("members/<int:id>/products/add/", views.add_product, name="add_product"),
    path("members/<int:id>/products/<int:product_id>/edit/", views.edit_product, name="edit_product"),
    path("members/<int:id>/products/<int:product_id>/delete/", views.delete_product, name="delete_product"),

    # Tiện ích
    path("download_vcf/<int:id>/", views.download_vcf, name="download_vcf"),
    path("qr/<int:id>/", views.qr_code, name="qr_code"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
