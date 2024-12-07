from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Login
from .serializers import LoginSerializer
import logging
from company.models import CompanyDetails
from employee.models import EmpWorkDetails
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
import logging

logger = logging.getLogger(__name__)

class RegisterAdminAccountManager(APIView):
    @transaction.atomic
    def post(self, request):
        data = request.data
        # Ensure role is not 'employee' before proceeding
        role = data.get('role')
        if role == 'employee':
            return Response({"error": "Role cannot be 'employee' for this endpoint."}, status=status.HTTP_400_BAD_REQUEST)
        
        # If role is valid, proceed to save
        serializer = LoginSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class RegisterEmployee(APIView):
    permission_classes = [IsAuthenticated]  

    @transaction.atomic
    def post(self, request):
        data = request.data
        email = data.get('email')
        
        # Check if the email exists in EmpWorkDetails first
        emp_work_details = EmpWorkDetails.objects.filter(companyEmailId=email).first()

        if emp_work_details:
            # If employee exists in EmpWorkDetails, create the employee record
            data['role'] = 'employee'
            serializer = LoginSerializer(data=data)

            if serializer.is_valid():
                # Save the employee
                employee = serializer.save()
                
                # Assign the employee ID to the EmpWorkDetails
                emp_work_details.userId = employee
                emp_work_details.save()
                logger.info(f"Employee created and linked to EmpWorkDetails for email: {email}")

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # If employee does not exist in EmpWorkDetails
            return Response({"error": "Employee does not exist in the system. Please create the employee first."},
                            status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Find the user by email
        user = Login.objects.filter(email=email).first()

        if user and check_password(password, user.password):
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            # Add 'role' to the JWT payload
            access.payload['role'] = user.role  # Add the role to the payload

            # Prepare the response data
            response_data = {
                'refresh': str(refresh),
                'access': str(access),
                'role': user.role,
            }

            # Add role-specific data if necessary (dynamically based on role)
            if user.role != 'employee':
                # Add role-specific fields only for non-employee roles
                if hasattr(user, 'is_company_setup_complete'):
                    response_data['is_company_setup_complete'] = user.is_company_setup_complete
                if hasattr(user, 'is_payroll_setup_complete'):
                    response_data['is_payroll_setup_complete'] = user.is_payroll_setup_complete

            return Response(response_data, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)




class CompanyStatusView(APIView):
    def get(self, request, user_id):
        user = Login.objects.get(id=user_id)
        if user.company:  # Ensure user has an associated company
            company = user.company
            company_status = {
                'company_setup_done': company.isCompanyDetailsCompleted,  # Ensure field exists in CompanyDetails
                'payroll_setup_done': company.payroll_done,  # Ensure field exists in CompanyDetails
                'employee_setup_done': company.employee_setup_done,  # Ensure field exists in CompanyDetails
            }
            return Response(company_status, status=status.HTTP_200_OK)
        return Response({"error": "Company setup not found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, user_id):
        user = Login.objects.get(id=user_id)  # Fetch the user

        company_id = request.data.get('company_id')
        if not company_id:
            return Response({"error": "Company ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Use companyId instead of id
            company = CompanyDetails.objects.get(companyId=company_id)  # Fetch the company by companyId
        except CompanyDetails.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

        # Link company to user
        user.company_id = company.companyId
        user.is_company_setup_complete = True  # Mark the company setup as complete
        # user.role = "admin"
        # user.is_admin = True
        user.save()

        return Response({"message": "Company setup updated successfully"}, status=status.HTTP_200_OK)



class GetCompanyIdView(APIView):

    def get(self, request, user_id):
        try:
            # Fetch the user by ID
            user = Login.objects.get(id=user_id)
            # Get the associated companyId if the user has a linked company
            company_id = user.company.companyId if user.company else None

            if company_id:
                return Response({"companyId": company_id}, status=status.HTTP_200_OK)
            return Response({"error": "Company ID not found for this user"}, status=status.HTTP_404_NOT_FOUND)
        except Login.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class GetUserNameView(APIView):

    def get(self, request, user_id):
        try:
            # Fetch the user by ID
            user = Login.objects.get(id=user_id)
            # Get the associated companyId if the user has a linked company
            username = user.userName if user.userName else None

            if username:
                return Response({"username": username}, status=status.HTTP_200_OK)
            return Response({"error": "UserName not found for this user"}, status=status.HTTP_404_NOT_FOUND)
        except Login.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
