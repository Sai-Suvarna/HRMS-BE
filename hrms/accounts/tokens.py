from rest_framework_simplejwt.tokens import AccessToken

class CustomAccessToken(AccessToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        # Add custom claims here
        token['role'] = user.role if hasattr(user, 'role') else 'unknown'  
        return token


