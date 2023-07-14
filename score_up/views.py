from django.shortcuts import render, redirect
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
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile, Letter
import json
from django.core.files import File
import os
from django.conf import settings
from datetime import datetime
from rest_framework.decorators import api_view
from django.http import HttpResponse




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
            'id': user.id,
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
        return JsonResponse({'items': credit_check_item}, safe=False)

class DisputeReasonItemView(View):
    def get(self, request):
        dispute_item = ["This inquiry is not authorized, please remove it. (Recommended)", "Please verify this information or remove it.", "This information is due to identity theft, please remove it."]
        # convert your list to json and return it
        return JsonResponse({'details': dispute_item}, safe=False)
    
class EmailTemplateItemView(View):
    def get(self, request):
        identity_theft_letter = Path('score_up/dispute letters/identity-theft.txt').read_text().replace('\n', '<br/>')
        unauthorized_inquiry_letter = Path('score_up/dispute letters/unauthorized-inquiry.txt').read_text().replace('\n', '<br/>')
        verify_information_letter = Path('score_up/dispute letters/verify-information.txt').read_text().replace('\n', '<br/>')
        email_template_item = {
            "This inquiry is not authorized, please remove it. (Recommended)": unauthorized_inquiry_letter, 
            "Please verify this information or remove it.": verify_information_letter, 
            "This information is due to identity theft, please remove it.": identity_theft_letter
        }
        return JsonResponse({'labels': email_template_item}, safe=False)

@csrf_exempt
def upload_user_images(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method. POST required.'}, status=400)

    user_id = request.POST.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required.'}, status=400)

    file_type = request.POST.get('file_type')  
    if not file_type:
        return JsonResponse({'error': 'fileType is required.'}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'error': f'User with id {user_id} does not exist.'}, status=400)

    user_profile, created = UserProfile.objects.get_or_create(user=user)

    for key in request.FILES.keys():
        if 'file' in key:  # Assuming keys are 'file0', 'file1', etc.
            file = request.FILES[key]
            if file_type == 'drivers_license':
                user_profile.drivers_license = file
            elif file_type == 'utility_bill':
                user_profile.utility_bill = file
            else:
                return JsonResponse({'error': f'Invalid file type {file_type}. Expected drivers_license or utility_bill.'}, status=400)

    user_profile.save()

    return JsonResponse({'message': 'Images uploaded successfully.'}, status=200)


@csrf_exempt
def get_user_images(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Invalid request method. GET required.'}, status=400)

    user_id = request.GET.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id is required.'}, status=400)

    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
    except UserProfile.DoesNotExist:
        return JsonResponse({
            'drivers_license': '',
            'utility_bill': '',
        })

    drivers_license_image_path = user_profile.drivers_license.url if user_profile.drivers_license else ''
    utility_bill_image_path = user_profile.utility_bill.url if user_profile.utility_bill else ''

    return JsonResponse({
        'drivers_license': drivers_license_image_path,
        'utility_bill': utility_bill_image_path,
    })

@csrf_exempt
def save_letter(request):
    if request.method == "POST":
        data = json.loads(request.body)
        letter_text = data.get('letter', '')
        dispute_reason = data.get('dispute_reason', '')
        user_id = data.get('user_id', '')
        letter_sent = data.get('letter_sent', '')

        # get current time and format it as a string
        dateTime = datetime.now()
        now = dateTime.strftime("%Y%m%d%H%M%S")
        letter_filename = f"{user_id}_{now}_letter.txt"  
        letter_filepath = os.path.join(settings.MEDIA_ROOT, 'letters', letter_filename)

        with open(letter_filepath, 'w') as f:
            myfile = File(f)
            myfile.write(letter_text)

        letter = Letter.objects.create(
            user_id=user_id,
            letter_file=os.path.join('letters', letter_filename),
            dispute_reason=dispute_reason,
            letter_sent=letter_sent,
            date_time=dateTime
        )

        return JsonResponse({"success": True, "letter_url": letter.letter_file.url})

@csrf_exempt
def get_letters(request):
    user_id = request.GET.get('user_id')
    letters = Letter.objects.filter(user_id=user_id)
    data = []

    for letter in letters:
        item = {
            "id": letter.id,
            "name": os.path.basename(letter.letter_file.name),
            "path": letter.letter_file.url,
            "created": letter.date_time.isoformat() if letter.date_time else None,
            "status": letter.letter_sent,
            "item_disputed": letter.dispute_reason,
        }
        data.append(item)

    return JsonResponse(data, safe=False)

@api_view(['DELETE'])
def delete_letter(request):
    try:
        data = json.loads(request.body)
        id = data.get('id', '')
        # get the Letter object
        letter = Letter.objects.get(id=id)

        # delete the file associated with the letter
        if os.path.isfile(letter.letter_file.path):
            os.remove(letter.letter_file.path)

        # delete the Letter object, which should also remove the record from the database
        letter.delete()

        return HttpResponse(status=204)
    except Letter.DoesNotExist:
        return HttpResponse(status=404)