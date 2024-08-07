#! This view helps to send CSRF token to frontend
from django.middleware.csrf import get_token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny


class CsrfTokenViews(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            csrf_token = get_token(request)
            response = Response({'csrfToken': csrf_token})
            response.set_cookie('csrftoken', csrf_token, max_age=31449600, secure=True, httponly=True, samesite='None')
            return response
        except Exception as e:
            return Response({'responseErrorMessage': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)