from home.models import *
from django.http import JsonResponse
import json
from datetime import timedelta, datetime
from django.utils import timezone
import jwt
from core.settings import SECRET_KEY

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
    company = request.POST.get('company')
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
            token = generate_jwt_token(email_id,user_exists.user_type,company)
            response = JsonResponse({"SUCCESS": {
                'email': email_id,
                'userType': user_exists.user_type,
                "message" : "OTP verified successfully",
                "company" : user_exists.company_id,
                "token" : token
            }}, status=200)
            return response
        else :
            return JsonResponse({"ERROR": "User not registered"}, status=400)
        
    
    except OTPRegistration.DoesNotExist:
        return JsonResponse({"ERROR": "No OTP found for this email"}, status=404)

def check_login_loader(request):
    if hasattr(request, 'user_email'):
        return JsonResponse({'SUCCESS': {
                'email': request.user_email,
                'userType': request.userType,
                'company' : request.company,
                "message" : "User is login"
            }})
    else:
        return JsonResponse({'Error': 'Unauthorized access, please log in'}, status=401)

def get_loadplan_loaders(request):
    if hasattr(request, 'userType') and request.userType == "Company_loader":
        try:
            email = request.user_email
            loader = Users.objects.get(email_id=email)

            # Fetch all load plan assignments for the loader, including plan_id, assignee, and assigned_at
            load_plan_assignments = LoadPlanAssignment.objects.filter(assigned_user=loader).select_related('load_plan', 'assignee')

            if not load_plan_assignments.exists():
                return JsonResponse({"ERROR": "No load plans assigned to this loader"}, status=404)

            # Prepare the result with plan_id, assigned_at, and assignee's email_id
            result = [
                {
                    "plan_id": assignment.load_plan.plan_id,
                    "assigned_at": assignment.assigned_at,
                    "assignee": assignment.assignee.email_id
                }
                for assignment in load_plan_assignments
            ]

            return JsonResponse({
                "SUCCESS": {
                    "message": "Load plans fetched successfully",
                    "result": result
                }
            }, status=200)
        except Users.DoesNotExist:
            return JsonResponse({"ERROR": "Loader user not found"}, status=404)

        except Exception as e:
            return JsonResponse({"ERROR": str(e)}, status=500)
    return JsonResponse({"ERROR": "Unauthorized access, Loader user can assign loadplan"}, status=403)

def get_order_details(request):
    if request.method == "POST":
        if hasattr(request, 'userType') and request.userType == "Company_loader":
            try:
                data = json.loads(request.body)
                plan_id = data.get("plan_id")
                company_name = request.company
       
                if not plan_id:
                    return JsonResponse({"ERROR": "plan_id is required"}, status=400)

                load_plan = LoadPlan.objects.filter(plan_id=plan_id, company__company_name=company_name).first()

                if not load_plan:
                    return JsonResponse({"ERROR": "Load plan not found for this company"}, status=404)

                order_numbers = load_plan.order_numbers
                print(order_numbers)

                orders = Order.objects.filter(order_number__in=order_numbers, company=load_plan.company)

                if not orders.exists():
                    return JsonResponse({"ERROR": "No orders found for the given load plan"}, status=404)

                result = {}

                for order in orders:
                    order_skus = OrderSKU.objects.filter(order=order, company=load_plan.company)

                    skus_data = []
                    for order_sku in order_skus:
                        skus_data.append({
                            "sku_code": order_sku.sku.sku_code,
                            "sku_name": order_sku.sku.sku_name,
                            "quantity": order_sku.quantity,
                            "gross_weight": order_sku.sku.gross_weight,
                            "length": order_sku.sku.length,
                            "width": order_sku.sku.width,
                            "height": order_sku.sku.height,
                            "volume": order_sku.sku.volume,
                            "tilt_allowed": order_sku.sku.tiltAllowed,
                        })

                    # Assign the list of SKU data to the corresponding order_id in the result
                    result[order.order_number] = skus_data

                return JsonResponse({
                    "SUCCESS": {
                        "message": "Order and SKU details fetched successfully",
                        "result": result
                    }
                }, status=200)

            except Exception as e:
                print(str(e))
                return JsonResponse({"ERROR": str(e)}, status=500)
        return JsonResponse({"ERROR": "Unauthorized access, Loader user can assign loadplan"}, status=403)
    return JsonResponse({"ERROR": "Invalid request method"}, status=405)
