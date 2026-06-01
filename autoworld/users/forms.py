import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import UserProfile


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(
        label='Логин или E-mail',
        widget=forms.TextInput(attrs={'class': 'form-input', 'autofocus': True}),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
    )


class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-input'}),
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Логин',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Пользователь с таким E-mail уже зарегистрирован')
        return email


class ProfileUserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name')
        labels = {
            'username': 'Логин',
            'email': 'E-mail',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        exists = get_user_model().objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists()
        if exists:
            raise forms.ValidationError('Этот E-mail уже используется другим пользователем')
        return email


class UserProfileForm(forms.ModelForm):
    this_year = datetime.date.today().year
    date_birth = forms.DateField(
        label='Дата рождения',
        required=False,
        widget=forms.SelectDateWidget(years=tuple(range(this_year - 100, this_year - 5))),
    )

    class Meta:
        model = UserProfile
        fields = ('photo', 'date_birth')
        labels = {
            'photo': 'Фотография',
        }
