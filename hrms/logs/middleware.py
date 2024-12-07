# import jwt
# from django.conf import settings
# from .models import TransactionLog

# class TransactionLogMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Process request
#         response = self.get_response(request)
#         print("Response:", response)

#         # Log transaction if userId is available
#         auth_header = request.headers.get('Authorization', None)
#         if auth_header and auth_header.startswith("Bearer "):
#             try:
#                 token = auth_header.split()[1]
#                 decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
#                 user_id = decoded_token.get("user_id")  # Adjust this based on your JWT structure

#                 TransactionLog.objects.create(
#                     user_id=user_id,
#                     action=f"{request.method} {request.path}",
#                     endpoint=request.path,
#                     method=request.method,
#                     details=request.body.decode('utf-8') if request.body else None
#                 )
#             except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception) as e:
#                 # Log only valid requests; ignore token errors
#                 pass

#         return response


import jwt
from django.conf import settings
from .models import TransactionLog

class TransactionLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Log transaction if userId is available
        auth_header = request.headers.get('Authorization', None)
        if auth_header and auth_header.startswith("Bearer "):
            try:
                # Decode JWT token
                token = auth_header.split()[1]
                decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = decoded_token.get("user_id")  # Adjust this based on your JWT structure

                # Read request data
                if request.method in ['POST', 'PUT', 'PATCH']:
                    # Use DRF's parsed data if available
                    details = getattr(request, 'data', None)  # Parsed JSON or form data
                else:
                    details = None  # No body for GET or other methods

                # Log the transaction
                TransactionLog.objects.create(
                    user_id=user_id,
                    action=f"{request.method} {request.path}",
                    endpoint=request.path,
                    method=request.method,
                    details=details if details else None,
                )
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception) as e:
                print(f"JWT Error: {e}")  # Debugging output; remove in production

        return response
