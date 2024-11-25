from django.shortcuts import render,redirect
from django.http import HttpResponse ##used for direct returning the html tags.
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.hashers import make_password
from home.models import *
from django.contrib import messages
from django.db import IntegrityError
from home.decorators import custom_login_required
import random
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
import json
from home.utils import save_data_to_files,DataProcess,perform_computation
from copy import deepcopy
import pandas as pd
import math
import re
from django.views.decorators.csrf import csrf_protect
import numpy as np
from django.core.mail import send_mail
from django.utils import timezone
import os
import jwt
from datetime import timedelta, datetime
from core.settings import SECRET_KEY,DEFAULT_FROM_EMAIL,BASE_DIR, STATIC_URL,AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY,AWS_STORAGE_BUCKET_NAME,AWS_S3_REGION_NAME,AWS_S3_CUSTOM_DOMAIN
import boto3
import uuid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from botocore.exceptions import ClientError
truck_specs = {
    "General Purpose container 20'": {
        "length_container":5900,
        "width_container":2352,
        "height_container":2393,
        "max_weight": 32500,
        # Add more specifications as needed
    },
    "General Purpose container 40'": {
        "length_container":12032,
        "width_container":2352,
        "height_container":2395,
        "max_weight": 32500,
        # Add more specifications as needed
    },
    "High - Cube General Purpose container 40'": {
        "length_container":12032,
        "width_container":2432,
        "height_container":2700,
        "max_weight": 32500,
    },
    # Add more specifications as needed
}



def generate_jwt_token(email_id,userType,company):
    expiration_time = datetime.utcnow() + timedelta(hours=5)
    payload = {
        'email': email_id,
        'userType':userType,
        "company":company,
        'exp': expiration_time  # Expiration time for the token
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token
def login_viewJson(request):
    if request.method == "POST":
        if hasattr(request, 'user_email'):
            return JsonResponse({'ERROR': f'Already logged in as {request.user_email}!'})
        email = request.POST.get('email')
        password = request.POST.get('password')
        company = request.POST.get("company_name")
        if not email or not password:
            messages.error(request, "Email and password are required.")
            return JsonResponse({"ERROR": "Email and password are required."}, status=400)
        user_exists = Users.objects.filter(email_id=email).first()
        if not user_exists:
            return JsonResponse({"ERROR": "User not registered"}, status=400)
        if user_exists.is_password == False:
            return JsonResponse({"ERROR": "Password is not set. Set password or try OTP login."}, status=400)

        if check_password(password, user_exists.password):
            user_exists.is_authenticated= True
            user_exists.last_login = timezone.now()
            user_exists.user_status = "Active"
            user_exists.save()
            token = generate_jwt_token(email,user_exists.user_type,company)
            # next_url = request.GET.get('next', 'dashboard')  # Default to 'dashboard' if 'next' is not provided
            response = JsonResponse({"SUCCESS": {
                "user_id": user_exists.user_id,
                "isPassword": user_exists.is_password,
                'email': email,
                'userType': user_exists.user_type,
                "message" : "Login successfully",
                "company" : user_exists.company_id,
                "lastLogin": user_exists.last_login
            }}, status=200)
            response.set_cookie(
                'jwt_token',  
                token,        
                max_age=18000, 
                httponly=True, 
                secure=True,  
                samesite='None' 
            )
            return response
        else:
            return JsonResponse({"ERROR": "Authentication failed. Please try logging in again."}, status=400)

    return JsonResponse({"SUCCESS": "Login successfully"}, status=200)

def check_email(request):
    email_id = request.POST.get('email')
    user_exists = Users.objects.filter(email_id=email_id).exists()
    if user_exists:
        return JsonResponse({"ERROR": "User already exist try login"}, status=400)
    return JsonResponse({"SUCCESS": "Email is not register"}, status=400)
    
def send_otp_to_email(request):
    print(f"User email in view: {getattr(request, 'user_email', 'None')}")
    if hasattr(request, 'user_email'):
        return JsonResponse({'ERROR': f'Already logged in as {request.user_email}!'})
    # Step 1: Get the email from the request (assuming it's a POST request)
    email_id = request.POST.get('email')
    
    if not email_id:
        return JsonResponse({"ERROR": "Company Email is required"}, status=400)
    
    # Step 2: Generate a 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Step 3: Save OTP and email_id in the database
    otp_entry, created = OTPRegistration.objects.get_or_create(email_id=email_id)
    
    # If OTP entry exists, update the fields
    otp_entry.otp = otp
    otp_entry.isVerified = False
    otp_entry.otp_sent_time = timezone.now()
    otp_entry.expired = False
    otp_entry.save()

    # Step 4: Send the OTP via email
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}. It is valid for 15 minutes.'
    email_from = DEFAULT_FROM_EMAIL
    recipient_list = [email_id]
    print("email",email_from)
    try:
        send_mail(subject, message, email_from, recipient_list)
        return JsonResponse({"SUCCESS": "OTP send successfully","sendTime":f"{otp_entry.otp_sent_time}"}, status=200)
    except Exception as e:
        return JsonResponse({"ERROR": f"Failed to send OTP. Error: {str(e)}"}, status=500)

def verify_otp(request):
    # Step 1: Get the email and otp from the request
    email_id = request.POST.get('email')
    otp_input = request.POST.get('otp')
    companyname = request.POST.get('company_name')
    
    if not email_id or not otp_input:
        return JsonResponse({"ERROR": "Email and OTP are required"}, status=400)
    
    try:
        # Step 2: Fetch the latest OTP entry for the given email
        otp_entry = OTPRegistration.objects.filter(email_id=email_id).latest('otp_sent_time')
        
        # Step 5: Check if the OTP is valid
        if otp_entry.otp != otp_input:
            return JsonResponse({"ERROR": "Invalid OTP"}, status=400)
        # Step 3: Check if the OTP has already been verified
        if otp_entry.isVerified:
            return JsonResponse({"ERROR": "OTP has already been verified"}, status=400)
        time_difference = timezone.now() - otp_entry.otp_sent_time
        # Step 4: Check if the OTP is expired
        if otp_entry.expired:
            return JsonResponse({"ERROR": "OTP has expired"}, status=400)
        
        if time_difference > timedelta(minutes=15):
            # Mark the OTP as expired
            otp_entry.expired = True
            otp_entry.save()
            return JsonResponse({"ERROR": "OTP has expired"}, status=400)
        
        # Step 6: Mark OTP as verified
        otp_entry.isVerified = True
        otp_entry.save()
        company, created = Company.objects.get_or_create(company_name=companyname)
    
        if created and not company.company_code:
            company.company_code = uuid.uuid4()
            company.save()
        for container_name, specs in truck_specs.items():
            Container.objects.create(
                container_id=uuid.uuid4(),
                container_name=container_name,
                container_length=specs["length_container"],
                container_width=specs["width_container"],
                container_height=specs["height_container"],
                max_gross_weight=specs["max_weight"],
                container_volume=specs.get("container_volume", 0),
                company=company
            )
        # Determine user type based on user count
        if company.user_count == 0:
            user_type = "Company_Admin"
        else:
            user_type = "None"
        user = Users(
            email_id=email_id,
            user_id=uuid.uuid4(),
            user_first_name='DefaultFirstName',  # Replace with actual form data or defaults
            user_last_name='DefaultLastName',    # Replace with actual form data or defaults
            user_type=user_type,
            user_status='Active',
            is_authenticated=True,
            company=company,
            first_login = timezone.now()
        )
        user.save()

        # Update the user count in the company
        company.user_count += 1
        company.save()
        token = generate_jwt_token(email_id,user.user_type,companyname)
        print(token)
        response = JsonResponse({"SUCCESS": {
                "user_id": user.user_id,
                "isPassword": user.is_password,
                'email': email_id,
                'userType': user.user_type,
                "message" : "OTP verified successfully",
                "company" : user.company_id,
                "lastLogin":user.last_login,
                'image_url': user.user_image_url,
            }}, status=200)
        response.set_cookie(
            'jwt_token',  
            token,        
            max_age=3600, 
            httponly=True, 
            secure=True,  
            samesite='None' 
        )
        if user.user_type != "Company_Admin":
            admin_user = Users.objects.filter(company=company, user_type="Company_Admin").first()
            if admin_user:
                send_mail(
                    subject="New User Registered in Your Company",
                    message=f"A new user with email {email_id} has registered with your company '{companyname}'.",
                    from_email=DEFAULT_FROM_EMAIL,
                    recipient_list=[admin_user.email_id],  # Send to the company admin's email
                    fail_silently=False,
                )
        return response
    
    except OTPRegistration.DoesNotExist:
        return JsonResponse({"ERROR": "No OTP found for this email"}, status=404)

def verify_login(request):
    # Step 1: Get the email and otp from the request
    email_id = request.POST.get('email')
    otp_input = request.POST.get('otp')
    company = request.POST.get("company_name")
    if not email_id or not otp_input:
        return JsonResponse({"ERROR": "Email and OTP are required"}, status=400)
    
    user_exists = Users.objects.filter(email_id=email_id).first()
    if not user_exists:
        return JsonResponse({"ERROR": "User not registered"}, status=400)
    try:
        # Step 2: Fetch the latest OTP entry for the given email
        otp_entry = OTPRegistration.objects.filter(email_id=email_id).latest('otp_sent_time')
        
        # Step 5: Check if the OTP is valid
        if otp_entry.otp != otp_input:
            return JsonResponse({"ERROR": "Invalid OTP"}, status=400)
        # Step 3: Check if the OTP has already been verified
        if otp_entry.isVerified:
            return JsonResponse({"ERROR": "OTP has already been verified"}, status=400)
        time_difference = timezone.now() - otp_entry.otp_sent_time
        # Step 4: Check if the OTP is expired
        if otp_entry.expired:
            return JsonResponse({"ERROR": "OTP has expired"}, status=400)
        
        if time_difference > timedelta(minutes=15):
            # Mark the OTP as expired
            otp_entry.expired = True
            otp_entry.save()
            return JsonResponse({"ERROR": "OTP has expired"}, status=400)
        
        # Step 6: Mark OTP as verified
        otp_entry.isVerified = True
        otp_entry.save()
        if user_exists:
            user_exists.last_login = timezone.now()
            user_exists.user_status = "Active"
            user_exists.save()
            token = generate_jwt_token(email_id,user_exists.user_type,company)
            response = JsonResponse({"SUCCESS": {
                "user_id": user_exists.user_id,
                "isPassword": user_exists.is_password,
                'email': email_id,
                'userType': user_exists.user_type,
                "message" : "OTP verified successfully",
                "company" : user_exists.company_id,
                "lastLogin": user_exists.last_login,
                'image_url': user_exists.user_image_url,
            }}, status=200)
            response.set_cookie(
                'jwt_token',  
                token,        
                max_age=18000, 
                httponly=True, 
                secure=True,  
                samesite='None' 
            )
            return response
        else :
            return JsonResponse({"ERROR": "User not registered"}, status=400)
        
    
    except OTPRegistration.DoesNotExist:
        return JsonResponse({"ERROR": "No OTP found for this email"}, status=404)

def logout_user(request):
    if request.method == 'POST':
        token = request.token
        if token:
            token = token.split(' ')[1] if ' ' in token else token
            response = JsonResponse({"SUCCESS": {"message":"Logged out successfully"}}, status=200)
            response.set_cookie(
                'jwt_token',  
                '',        
                max_age=0, 
                httponly=True, 
                secure=True,  
                samesite='None' 
            )
            return response
        return JsonResponse({"ERROR": "Token not provided"}, status=400)
    return JsonResponse({"ERROR": "Invalid request method"}, status=405)

def check_login(request):
    if hasattr(request, 'user_email'):
        user = Users.objects.get(email_id=request.user_email)
            
        return JsonResponse({
            'SUCCESS': {
                "user_id": user.user_id,
                "isPassword": user.is_password,
                'email': user.email_id,
                'userType': user.user_type,
                # 'company': user.company.company_name if user.company else None,
                'message': "User is logged in",
                'image_url': user.user_image_url,
                "lastLogin": user.last_login
            }
        })
    else:
        return JsonResponse({'Error': 'Unauthorized access, please log in'}, status=401)
def set_password(request):
    if request.method == 'POST':
        user_id = request.POST.get('userId')
        password = request.POST.get('password')
        if not user_id or not password:
            return JsonResponse({"ERROR": "Missing userId or password"}, status=400)
        try: 
            user = Users.objects.get(user_id=user_id)
            user.password = make_password(password)
            user.is_password = True
            user.save()

            return JsonResponse({"SUCCESS": {"message":"Password set successfully"}}, status=200)
        
        except Users.DoesNotExist:
            return JsonResponse({"ERROR": "User not found"}, status=404)
    return JsonResponse({"ERROR": "Invalid request method"}, status=405)

