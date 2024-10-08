import jwt
from core.settings import SECRET_KEY
from django.http import JsonResponse
from jwt import ExpiredSignatureError, DecodeError

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.COOKIES.get('jwt_token')  # Extract the JWT from the cookie
        print("cookie")
        print(token)
        protected_paths = [
            '/dashboard_admin',
        ]
        bypass_paths = [
            '/send_otp_to_email'
        ]
        if any(request.path.startswith(path) for path in protected_paths):
            token = request.COOKIES.get('jwt_token')  # Extract the JWT from the cookie

            if token:
                try:
                    # Decode the JWT token
                    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                    
                    # Add the decoded email or other user details to the request object
                    print(payload.get('email'))
                    request.user_email = payload.get('email')
                    print(payload)
                    print(f"User email set: {request.user_email}")

                except jwt.ExpiredSignatureError:
                    return JsonResponse({"ERROR": "Login sessioin has expired. Login again"}, status=401)
                except jwt.DecodeError:
                    return JsonResponse({"ERROR": "Invalid token"}, status=401)
            else:
                return JsonResponse({"ERROR": "Token required"}, status=401)
        if any(request.path.startswith(path) for path in bypass_paths):
            token = request.COOKIES.get('jwt_token')
            if token:
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                request.user_email = payload.get('email')
            print("Bypassing JWT authentication for:", request.path)
        # Proceed with the request if no token or valid token
        response = self.get_response(request)
        return response