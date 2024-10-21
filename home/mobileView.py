from home.models import *
from django.http import JsonResponse
import json

def check_email_loaders(request):
    if request.method == 'POST':
        email_id = request.POST.get('email')
        
        try:
            user = Users.objects.filter(email_id=email_id).first()
            
            if not user:
                return JsonResponse({"ERROR": "User not found"}, status=404)
            
            if user.user_type != "Company_loader":
                return JsonResponse({"ERROR": "User is not a loader"}, status=400)
            
            return JsonResponse({"SUCCESS": {"message": "Loader exist","result": {
                'email': email_id,
                'userType': user.user_type,
                "message" : "Loader exist",
                "company" : user.company_id
            }}}, status=200)
        
        except Exception as e:
            return JsonResponse({"ERROR": str(e)}, status=500)
    
    return JsonResponse({"ERROR": "Invalid request method"}, status=405)

def verify_loader(request):
    
    email_id = request.POST.get('email')
    otp_input = request.POST.get('otp')
    if not email_id or not otp_input:
        return JsonResponse({"ERROR": "Email and OTP are required"}, status=400)
    
    user_exists = Users.objects.filter(email_id=email_id).first()
    if not user_exists:
        return JsonResponse({"ERROR": "User is not added by admin"}, status=400)
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
            # token = generate_jwt_token(email_id,user_exists.user_type,company)
            response = JsonResponse({"SUCCESS": {
                'email': email_id,
                'userType': user_exists.user_type,
                "message" : "OTP verified successfully",
                "company" : user_exists.company_id
            }}, status=200)
            # response.set_cookie(
            #     'jwt_token',  
            #     token,        
            #     max_age=18000, 
            #     httponly=True, 
            #     secure=True,  
            #     samesite='None' 
            # )
            return response
        else :
            return JsonResponse({"ERROR": "User not registered"}, status=400)
        
    
    except OTPRegistration.DoesNotExist:
        return JsonResponse({"ERROR": "No OTP found for this email"}, status=404)

    