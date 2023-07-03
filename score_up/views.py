from django.shortcuts import render, redirect
from score_up.forms import MyCustomSignupForm
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class SignupView(APIView):
    def post(self, request):
        password = request.data.get("password")
        email = request.data.get("email")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        
        # Check if a user already exists with this email
        if User.objects.filter(email=email).exists():
            return Response({"error": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a new user
        user = User.objects.create_user(email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Generate a refresh token for this new user
        refresh = RefreshToken.for_user(user)

        # Include the tokens in the response
        return Response({
            'message': 'User created successfully',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, username=email, password=password)

        if user is not None:
            # The user was successfully authenticated. 
            # Generate a refresh token for this user
            refresh = RefreshToken.for_user(user)

            # Include the tokens in the response
            return Response({
                'message': 'Login successful',
                'name': user.first_name,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            # Authentication failed
            return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

        
def frontpage(request):
        return render(request, 'frontpage.html')