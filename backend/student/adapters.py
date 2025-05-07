from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Optional: override this if you want to customize user creation
    """
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        # Check if email is missing
        if not user.email:
            raise ValueError("Email not provided by social account")

        return user

class JWTEnabledSocialLoginView(SocialLoginView):
    """
    Override SocialLoginView to return JWT tokens instead of session
    """
    def get_response(self):
        # original user login logic
        original_response = super().get_response()
        user = self.user
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })
