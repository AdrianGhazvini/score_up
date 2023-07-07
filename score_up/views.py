from django.shortcuts import render, redirect
from score_up.forms import MyCustomSignupForm
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions
from django.http import JsonResponse
from django.views import View
from pathlib import Path



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
        user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
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

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = User.objects.get(email=request.user.email)
        return Response({
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }, status=status.HTTP_200_OK)
    
def frontpage(request):
        return render(request, 'frontpage.html')

class CreditCheckItemView(View):
    def get(self, request):
        credit_check_item = ["EQF Software Quality - Credit Inquiry", "CBCINNOVIS - Credit Inquiry", "United Bank - Consumer Account"]

        # convert your list to json and return it
        return JsonResponse({'labels': credit_check_item}, safe=False)

class DisputeReasonItemView(View):
    def get(self, request):
        dispute_item = ["This inquiry is not authorized, please remove it. (Recommended)", " Please verify this information or remove it.", "This information is due to identity theft, please remove it."]
        # convert your list to json and return it
        return JsonResponse({'details': dispute_item}, safe=False)
    
class EmailTemplateItemView(View):
    def get(self, request):
        #identity_theft_letter = Path('dispute letters/identity-theft.txt').read_text()
        unauthorized_inquiry_letter = Path('score_up/dispute letters/unauthorized-inquiry.txt').read_text()
        #verify_information_letter = Path('dispute letters/verify-information.txt').read_text()
        #email_template_item = [identity_theft_letter, unauthorized_inquiry_letter, verify_information_letter ]
        email_template_item = unauthorized_inquiry_letter
        # convert your list to json and return it
        return JsonResponse({'labels': email_template_item}, safe=False)