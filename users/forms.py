from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

User = get_user_model()

#Form for user registration
class UserRegisterForm(UserCreationForm):
    #Add additional fields to reg form
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        #ADd sign up button to form
        self.helper.add_input(Submit('submit', 'Sign Up'))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


#Form for updating user info
class UserUpdateForm(forms.ModelForm):
    #Add additional fields to form
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

#Form for updating profile info
class ProfileUpdateForm(forms.ModelForm):
    #predefined choices fro job rol
    job_role = forms.ChoiceField(choices=Profile.JOB_ROLE_CHOICES)

    class Meta:
        model = Profile
        fields = ['image', 'job_role']