from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Profile


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. dev_candidate'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'e.g. name@domain.com'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email


    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError({"password_confirm": "Passwords do not match."})

            # Length check
            if len(password) < 8:
                raise forms.ValidationError({"password": "Password must be at least 8 characters long."})
            
            # Character sets checks
            if not any(c.isupper() for c in password):
                raise forms.ValidationError({"password": "Password must contain at least one uppercase letter."})
            if not any(c.islower() for c in password):
                raise forms.ValidationError({"password": "Password must contain at least one lowercase letter."})
            if not any(c.isdigit() for c in password):
                raise forms.ValidationError({"password": "Password must contain at least one number."})
            if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password):
                raise forms.ValidationError({"password": "Password must contain at least one special character."})

            # Django system-wide password validation rules
            from django.contrib.auth.password_validation import validate_password
            try:
                validate_password(password)
            except forms.ValidationError as ve:
                raise forms.ValidationError({"password": ve.messages})
            except Exception as e:
                raise forms.ValidationError({"password": str(e)})

        return cleaned_data


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile

        fields = [
            'full_name',
            'professional_title',
            'phone',
            'location',
            'bio',
            'github',
            'linkedin',
            'portfolio_website',
            'profile_image',
            'cover_image',
            'leetcode_username',
            'codechef_username',
            'hackerrank_username'
        ]