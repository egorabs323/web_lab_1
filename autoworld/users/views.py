from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView

from .forms import LoginUserForm, ProfileUserForm, RegisterUserForm, UserProfileForm
from .models import UserProfile


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}


class LogoutUser(LogoutView):
    next_page = reverse_lazy('users:login')


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('cars:index')
    extra_context = {'title': 'Регистрация'}

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(self.request, 'Регистрация выполнена успешно')
        return response


class ProfileUser(LoginRequiredMixin, View):
    template_name = 'users/profile.html'

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        context = {
            'title': 'Профиль пользователя',
            'user_form': ProfileUserForm(instance=request.user),
            'profile_form': UserProfileForm(instance=profile),
            'default_image': settings.DEFAULT_USER_IMAGE,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        user_form = ProfileUserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль обновлен')
            return redirect('users:profile')

        context = {
            'title': 'Профиль пользователя',
            'user_form': user_form,
            'profile_form': profile_form,
            'default_image': settings.DEFAULT_USER_IMAGE,
        }
        return render(request, self.template_name, context)


class UserPasswordChange(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password_change_form.html'
    success_url = reverse_lazy('users:password_change_done')
    extra_context = {'title': 'Смена пароля'}

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Пароль успешно изменен')
        return response


class UserPasswordChangeDone(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = 'users/password_change_done.html'
    extra_context = {'title': 'Пароль изменен'}


class UserPasswordReset(PasswordResetView):
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')
    extra_context = {'title': 'Восстановление пароля'}


class UserPasswordResetDone(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'
    extra_context = {'title': 'Письмо отправлено'}


class UserPasswordResetConfirm(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')
    extra_context = {'title': 'Новый пароль'}


class UserPasswordResetComplete(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'
    extra_context = {'title': 'Пароль изменен'}
