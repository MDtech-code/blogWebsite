# Import TokenError from SimpleJWT exceptions
from rest_framework_simplejwt.exceptions import TokenError  
# Import AuthenticationFailed from DRF exceptions
from rest_framework.exceptions import AuthenticationFailed  
# Import Response class from DRF
from rest_framework.response import Response  
# Import status module from DRF for HTTP status codes
from rest_framework import status  

# Middleware class to handle JWT-related errors
class JWTErrorHandlingMiddleware:
    
    def __init__(self, get_response):
        # Initialize the middleware with the get_response callable
        self.get_response = get_response

    def __call__(self, request):
        # Callable method to process the request and return the response
        response = self.get_response(request)  # Get the response by calling the next middleware or view
        return response  # Return the response

    def process_exception(self, request, exception):
        # Method to handle exceptions that occur during request processing
        if isinstance(exception, (AuthenticationFailed, TokenError)):
            # Check if the exception is of type AuthenticationFailed or TokenError
            return Response(
                {'detail': 'Token has expired or is invalid'},  # Return a response with error detail
                status=status.HTTP_401_UNAUTHORIZED  # Set the status code to 401 Unauthorized
            )
        return None  # Return None if the exception is not handled


















'''
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework import status
class JWTErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        response = self.get_response(request)
        return response
    def process_exception(self, request, exception):
        if isinstance(exception, (AuthenticationFailed, TokenError)):
            return Response(
                {'detail': 'Token has expired or is invalid'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return None
'''