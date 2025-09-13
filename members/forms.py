from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "username", "password", "full_name", "position", "company",
            "avatar", "background",   
            "phone", "email", "website", "youtube", "zalo", "viber"
        ]
        widgets = {
            "password": forms.PasswordInput(render_value=True),
        }

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Profile
        fields = ["username", "password", "full_name", "email"]

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)