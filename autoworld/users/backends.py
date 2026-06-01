from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailAuthBackend(ModelBackend):
    """Авторизация по username или e-mail через стандартную модель User."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        login_value = username or kwargs.get(get_user_model().USERNAME_FIELD)
        if not login_value or not password:
            return None

        UserModel = get_user_model()
        lookup = {'email__iexact': login_value} if '@' in login_value else {'username__iexact': login_value}

        try:
            user = UserModel.objects.get(**lookup)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
            return None
        except UserModel.MultipleObjectsReturned:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
