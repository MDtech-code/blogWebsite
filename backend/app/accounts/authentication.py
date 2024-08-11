from rest_framework.authentication import BaseAuthentication, SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CombinedAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Try session authentication first
        session_auth = SessionAuthentication()
        user_session = session_auth.authenticate(request)
        
        # If session authentication fails, raise an exception
        if not user_session:
            raise AuthenticationFailed("Session authentication failed.")
        
        # Now check JWT authentication
        jwt_auth = JWTAuthentication()
        user_jwt = jwt_auth.authenticate(request)
        
        # If JWT authentication fails, raise an exception
        if not user_jwt:
            raise AuthenticationFailed("JWT authentication failed.")
        
        # If both succeed, return the user
        return user_session or user_jwt
