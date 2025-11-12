from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    phone = forms.CharField(
        required=True,
        max_length=10,
        min_length=10,
        help_text="Enter a 10-digit phone number"
    )
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name","phone", "email", "password1", "password2"]
        widgets={
            'username':forms.TextInput(attrs={'placeholder':'Username'}),
         
        }
        
    # UserCreationForm does not use Meta.widgets for password fields by default.
    # overriding it manually using __init__ function
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Password'
            
        })

        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm Password'
        
        })
        
        self.fields['phone'].widget.attrs.update({
            'placeholder':'Phone Number'
        })
    def clean_email(self):
            email = self.cleaned_data.get("email")
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("This email is already registered.")
            return email
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Check only digits and exactly 10 digits long
        if not re.match(r'^\d{10}$', phone):
            raise ValidationError("Phone number must be exactly 10 digits.")
        return phone
        