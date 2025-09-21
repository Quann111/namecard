from django import forms
from .models import Profile
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["title", "description", "thumbnail", "video_url"]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "username", "password", "full_name", "position", "company",
            "phone", "email", "website", "youtube", "zalo", "viber",
            # các cờ hiển thị nav
            "show_home", "show_intro", "show_products", "show_auth",
        ]
        widgets = {
            "password": forms.PasswordInput(render_value=True),
        }

    # Nếu bạn muốn bỏ qua validate trùng username khi edit chính mình
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if self.instance and self.instance.pk:
            if Profile.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
                raise forms.ValidationError("Tên đăng nhập này đã tồn tại.")
        return username


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Profile
        fields = ["username", "password", "full_name", "email"]


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)
