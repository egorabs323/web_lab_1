from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class LoginRequiredSiteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._login_required(request):
            login_url = reverse(settings.LOGIN_URL)
            return redirect(f'{login_url}?next={request.get_full_path()}')
        return self.get_response(request)

    def _login_required(self, request):
        if request.user.is_authenticated:
            return False

        path = request.path_info
        allowed_prefixes = (
            reverse('users:login'),
            reverse('users:register'),
            reverse('users:password_reset'),
            reverse('users:password_reset_done'),
            reverse('users:password_reset_complete'),
            settings.STATIC_URL,
            settings.MEDIA_URL,
            '/admin/login/',
        )

        if path.startswith('/users/reset/'):
            return False

        return not any(path.startswith(prefix) for prefix in allowed_prefixes)
