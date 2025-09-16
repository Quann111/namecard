from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("members/<int:id>/", views.details, name="details"),
    path("members/<int:id>/edit/", views.edit_profile, name="edit_profile"),
    path("members/", views.members, name="members"),
    path("template/", views.members, name="template"),
    path("download_vcf/<int:id>/", views.download_vcf, name="download_vcf"),
    path("qr/<int:id>/", views.qr_code, name="qr_code"),
    path("auth/", views.auth_tabs, name="auth_tabs")

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)