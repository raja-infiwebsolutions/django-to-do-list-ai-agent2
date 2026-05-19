"""Django forms for Todo and Authentication."""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Todo


class SignupForm(forms.Form):
    """User registration form."""
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
            'autocomplete': 'given-name',
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name',
            'autocomplete': 'family-name',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com',
            'autocomplete': 'email',
        })
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password (min 8 characters)',
            'autocomplete': 'new-password',
        })
    )
    password_confirm = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'autocomplete': 'new-password',
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password != password_confirm:
            raise ValidationError('Passwords do not match.')
        
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error('password', e)
        
        email = cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise ValidationError('Email already registered.')
        
        return cleaned_data


class LoginForm(forms.Form):
    """User login form."""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com',
            'autocomplete': 'email',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        })
    )


class TodoForm(forms.ModelForm):
    """Form for creating and editing todos."""
    
    class Meta:
        model = Todo
        fields = ['title', 'description', 'status', 'priority', 'due_date', 'completed']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Todo title',
                'required': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Add a description (optional)',
                'rows': 4,
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'completed': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError('Title is required.')
        return title
