from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.db.models import Q

User = get_user_model()


class MultiFieldAuthBackend(BaseBackend):

    def authenticate(self, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)

        try:
            user = User.objects.get(Q(username=username) | Q(email=username) | Q(phone_number=username))
        except User.DoesNotExist:
            return None

        if check_password(password, user.password):
            return user
        return None
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

