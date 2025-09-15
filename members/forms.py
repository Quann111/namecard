from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "username", "password", "full_name", "position", "company",
            "avatar", "background",   # ✅ phải có trong form thì mới upload ảnh mới được
            "phone", "email", "website", "youtube", "zalo", "viber"
        ]
        widgets = {
            # Dùng PasswordInput để che mật khẩu khi nhập
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
