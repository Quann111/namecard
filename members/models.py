from django.db import models
from django.contrib.auth.hashers import make_password
from cloudinary.models import CloudinaryField

class Profile(models.Model):
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    full_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=200, blank=True, null=True)

    # Ảnh đại diện và ảnh nền
    avatar = CloudinaryField("image", blank=True, null=True)
    background = CloudinaryField("image", blank=True, null=True)  # ✅ Ảnh nền lưu Cloudinary

    # Liên hệ
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    zalo = models.CharField(max_length=50, blank=True, null=True)
    viber = models.CharField(max_length=50, blank=True, null=True)

    # Quản trị
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk or not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Product(models.Model):
    owner = models.ForeignKey("Profile", on_delete=models.CASCADE, related_name="products")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)   # link Youtube/Vimeo
    thumbnail = models.ImageField(upload_to="products/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.owner.username})"
