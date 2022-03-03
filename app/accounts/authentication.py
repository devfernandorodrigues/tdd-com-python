from accounts.models import User, Token

class PasswordlessAuthenticationBackend:

    def authenticate(self, request, uid):
        try:
            token = Token.objects.get(uid=uid)
            user, _ = User.objects.get_or_create(email=token.email)
            return user
        except (Token.DoesNotExist):
            return None

    def get_user(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None
