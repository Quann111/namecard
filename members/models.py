from django.db import models
from django.contrib.auth.hashers import make_password

class Profile(models.Model):
    # Tài khoản
    username = models.CharField(max_length=50, unique=True)  # Tên đăng nhập duy nhất
    password = models.CharField(max_length=128)              # Mật khẩu (hash)

    # Thông tin cá nhân
    full_name = models.CharField(max_length=100)             
    position = models.CharField(max_length=100, blank=True, null=True)  
    company = models.CharField(max_length=200, blank=True, null=True)   
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)  
    
    # Liên hệ
    phone = models.CharField(max_length=20, blank=True, null=True)      
    email = models.EmailField(blank=True, null=True)                   
    website = models.URLField(blank=True, null=True)                   
    youtube = models.URLField(blank=True, null=True)                   
    zalo = models.CharField(max_length=50, blank=True, null=True)      
    viber = models.CharField(max_length=50, blank=True, null=True)     
    
    # Quản trị
    status = models.BooleanField(default=True)   # True = active, False = inactive
    created_at = models.DateTimeField(auto_now_add=True)               
    updated_at = models.DateTimeField(auto_now=True)                   

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Hash password nếu nhập password dạng plain text
        if not self.pk or not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

