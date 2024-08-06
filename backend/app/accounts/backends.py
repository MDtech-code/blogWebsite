from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailVerificationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserModel.objects.get(username=username)
            if user.check_password(password):
                if user.email_verified:
                    return user
                else:
                    raise PermissionError("Email not verified")
        except UserModel.DoesNotExist:
            return None
        except PermissionError as e:
            return None

    def user_can_authenticate(self, user):
        # Further checks can be added here if needed
        return super().user_can_authenticate(user)
