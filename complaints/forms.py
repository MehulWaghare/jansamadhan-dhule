from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from .models import Complaint, Comment


# ================= REGISTER =================
class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Email already registered!")
        return email


# ================= LOGIN =================
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control'
    }))


# ================= COMPLAINT =================
class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = [
            'title',
            'description',
            'category',
            'image',
            'latitude',
            'longitude',
            'address'
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter complaint title'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the problem clearly...'
            }),

            'category': forms.Select(attrs={
                'class': 'form-select'
            }),

            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),

            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'address': forms.HiddenInput(),
        }


# ================= COMMENT =================
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Write your comment...'
            })
        }