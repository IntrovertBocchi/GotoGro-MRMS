# members/forms.py

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Profile, Sale

# Form for registering new user
class UserRegisterForm(UserCreationForm):

    # Adding email field to registration form
    email = forms.EmailField(required=True)
    
    # Override password2 field to remove help text
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput,
        help_text=''  # Set help text to empty
    )

    class Meta:
        # Specifies user model to use and fields to include in the form
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
        help_texts = {
            'username': '',
            'password1': '',
        }

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')

        # Check minimum length
        if len(password1) < 8:
            raise forms.ValidationError("Your password must contain at least 8 characters.")

        # Check if the password is entirely numeric
        if password1.isdigit():
            raise forms.ValidationError("Your password cannot be entirely numeric.")

        # Check if the password is similar to personal information
        user_info = [username, email, first_name, last_name]
        for info in user_info:
            if info and info.lower() in password1.lower():
                raise forms.ValidationError("Your password cannot be too similar to your other personal information.")

        # Example of checking for common passwords (you could extend this with a list of common passwords)
        common_passwords = ['password', '123456', 'qwerty']
        if password1 in common_passwords:
            raise forms.ValidationError("Your password cannot be a commonly used password.")

        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        # Ensure the two passwords match
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields must match.")

        return cleaned_data

# Form for updating user information
class UserUpdateForm(forms.ModelForm):
    
    username = forms.CharField(
        help_text='',  # Set help text to empty
    )

    # Specifies to use user model and fields to include in the form
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


# Form to update profile model of a user
class ProfileUpdateForm(forms.ModelForm):
    
    class Meta:
        # Specifies profile model to use and the fields associated in this form
        model = Profile
        fields = ['address', 'phone_number', 'preferences']


class SaleUpdateForm(forms.ModelForm):
    
    class Meta:
        model = Sale
        fields = ['item_name', 'purchase_quantity', 'total_price']

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Old Password', widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')