from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from django.utils.translation import gettext as _
from rest_framework import exceptions
from jwt import InvalidTokenError
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import TokenError

# Custom JWT Authentication class
class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # Call the parent class's authenticate method
        super().authenticate(request)
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

    def get_validated_token(self, raw_token):
        # Validate the token and handle exceptions
        try:
            return UntypedToken(raw_token)
        except TokenError as e:
            raise exceptions.AuthenticationFailed(
                _('Invalid token.'),
                code='invalid_token',
            ) from e
        except InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(
                _('Token is invalid or expired'),
                code='token_not_valid',
            ) from e

    def get_user(self, validated_token):
        # Extract user information from the validated token
        try:
            user_id = validated_token['user_id']
        except KeyError:
            raise exceptions.AuthenticationFailed(
                _('Token contained no recognizable user identification'),
                code='invalid_token',
            )

        from .models import User  # Import here to avoid circular imports
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(
                _('User not found'),
                code='user_not_found',
            )

        if not user.is_active:
            raise exceptions.AuthenticationFailed(
                _('User is inactive'),
                code='user_inactive',
            )

        return user