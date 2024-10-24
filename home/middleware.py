import jwt
from core.settings import SECRET_KEY
from django.http import JsonResponse
from jwt import ExpiredSignatureError, DecodeError

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        protected_paths = [
            '/check_login',
            "/add_permission",
            "/get_permissions",
            "/add_loadplan",
            "/get_loadplan",
            "/add_container",
            "/get_container",
            "/send_email",
            "/get_allusers",
            "/get_usertype",
            "/update_usertype",
            "/remove_user",
            "/add_sku",
            "/get_sku",
            "/delete_sku",
            "/get_skuByCode",
            "/add_or_edit_order",
            "/get_containerByName",
            "/get_orderByNumber",
            "/attach_skus_to_order",
            "/get_skus_by_order_numbers",
            "/get_skuCodeAndName",
            "/create_load_plan",
            "/get_loaderUser",
            "/assign_load_plan",
            "/get_loadplan_loaders",
            "/check_login_loader",
            "/get_order_details",
        ]
        bypass_paths = [
            '/send_otp_to_email',
            '/verify_otp',
            '/verify_login',
            "/freeOutputJson",
            "/verify_loader",
            # "/upload_user_image",
        ]
        if any(request.path.startswith(path) for path in protected_paths):
            token = request.COOKIES.get('jwt_token')
            if not token:  
                token = request.headers.get('Authorization')
                if token:
                    token = token.split(' ')[1]
                    print("Native")
            print("cookie")
            print(token)  # Extract the JWT from the cookie

            if token:
                try:
                    # Decode the JWT token
                    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

                    # Add the decoded email or other user details to the request object
                    request.user_email = payload.get('email')
                    request.userType = payload.get('userType')
                    request.company = payload.get("company")
                    print(payload)

                except jwt.ExpiredSignatureError:
                    return JsonResponse({"ERROR": "Login sessioin has expired. Login again"}, status=401)
                except jwt.DecodeError:
                    return JsonResponse({"ERROR": "Invalid token"}, status=401)
            else:
                return JsonResponse({"ERROR": "Login sessioin has expired. Login again"}, status=401)
        if any(request.path.startswith(path) for path in bypass_paths):
            token = request.COOKIES.get('jwt_token')
            if not token:  
                token = request.headers.get('Authorization')
                if token:
                    token = token.split(' ')[1]
                    print("Native")
            print("cookie")
            print(token)
            if token:
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                request.user_email = payload.get('email')
                request.userType = payload.get('userType')
                request.company = payload.get("company")
            else :
                request.company =  ""
        # Proceed with the request if no token or valid token
        response = self.get_response(request)
        return response