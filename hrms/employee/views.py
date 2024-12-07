from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from company.models import CompanyDetails
from payrole.models import EmployeeCompensation
from rest_framework.exceptions import AuthenticationFailed

from .models import EmpWorkDetails, EmpSocialSecurityDetails, EmpPersonalDetails, EmpInsuranceDetails, EmpSalaryDetails
from .serializers import (
    EmpWorkDetailsSerializer, 
    EmpSocialSecurityDetailsSerializer, 
    EmpPersonalDetailsSerializer, 
    EmpInsuranceDetailsSerializer,
    EmpSalaryDetailsSerializer,
    CustomEmpWorkDetailsSerializer
)

class CombinedDetailsViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated] 

    @transaction.atomic
    def create(self, request):
        self.check_permissions(request)  # Check permissions before proceeding
        
        work_data = request.data.get('work_details')
        print("Work Data:",work_data)
        social_security_data = request.data.get('social_security_details')
        print("Social Data:",social_security_data)
        personal_data = request.data.get('personal_details')
        print("Personal data:",personal_data)
        insurance_data = request.data.get('insurance_details')
        print("Insurance data:",insurance_data)
        salary_data = request.data.get('salary_details')
        print("Salary data:",salary_data)

        # Check if company_id is provided
        company_id = request.data.get('company')  # This is passed from frontend (localStorage)
        if not company_id:
            return Response({"error": "Company ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the company instance using the company_id
            company = CompanyDetails.objects.get(companyId=company_id)
        except CompanyDetails.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

        # Step 1: Validate and save EmpWorkDetails
        work_serializer = EmpWorkDetailsSerializer(data=work_data)
        if not work_serializer.is_valid():
            return Response({
                "message": "Validation errors occurred.",
                "work_details_errors": work_serializer.errors,
                "social_security_details_errors": {},
                "personal_details_errors": {},
                "insurance_details_errors": {},
                "salary_details_errors": {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        work_instance = work_serializer.save(company=company)
        print("work instance",work_instance)

        try:
            # Step 2: Validate and save EmpSocialSecurityDetails
            social_security_data['wdId'] = work_instance.pk
            social_security_serializer = EmpSocialSecurityDetailsSerializer(data=social_security_data)
            if not social_security_serializer.is_valid():
                raise ValueError("Social security validation failed")
            social_security_instance = social_security_serializer.save()
            print("social",social_security_instance)

            # Step 3: Validate and save EmpPersonalDetails
            personal_data['wdId'] = work_instance.pk
            personal_serializer = EmpPersonalDetailsSerializer(data=personal_data)
            if not personal_serializer.is_valid():
                raise ValueError("Personal details validation failed")
            personal_instance = personal_serializer.save()
            print(personal_instance)

            # Step 4: Validate and save EmpInsuranceDetails
            insurance_data['wdId'] = work_instance.pk
            insurance_serializer = EmpInsuranceDetailsSerializer(data=insurance_data)
            if not insurance_serializer.is_valid():
                raise ValueError("Insurance details validation failed")
            insurance_instance = insurance_serializer.save()
            print(insurance_instance)

            # Step 5: Validate and save EmpSalaryDetailsSerializer
            salary_data['wdId'] = work_instance.pk
            salary_serializer = EmpSalaryDetailsSerializer(data=salary_data)
            if not salary_serializer.is_valid():
                raise ValueError("Insurance details validation failed")
            salary_instance = salary_serializer.save()
            print(salary_instance)

            # Here, handle reimbursements if they are included in the salary_data
            reimbursements = salary_data.get('reimbursements', {})
            if reimbursements:
                # Assuming salary_instance has a field for reimbursements
                salary_instance.reimbursements = reimbursements  # Ensure this field exists
                salary_instance.save()

        except ValueError as e:
            # If any validation fails, roll back the transaction
            transaction.set_rollback(True)
            return Response({
                "message": "Validation errors occurred.",
                "work_details_errors": {},
                "social_security_details_errors": social_security_serializer.errors if 'social_security_serializer' in locals() else {},
                "personal_details_errors": personal_serializer.errors if 'personal_serializer' in locals() else {},
                "insurance_details_errors": insurance_serializer.errors if 'insurance_serializer' in locals() else {},
                "salary_details_errors": salary_serializer.errors if 'salary_serializer' in locals() else {}
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "Successfully submitted all details."
        }, status=status.HTTP_201_CREATED)
  
    permission_classes = [IsAuthenticated] 

    def retrieve(self, request, pk=None):
        work_instance = get_object_or_404(EmpWorkDetails, pk=pk)
        social_security_instance = get_object_or_404(EmpSocialSecurityDetails, wdId=work_instance)
        personal_instance = get_object_or_404(EmpPersonalDetails, wdId=work_instance)
        insurance_instance = get_object_or_404(EmpInsuranceDetails, wdId=work_instance)
        salary_instance    = get_object_or_404(EmpSalaryDetails, wdId=work_instance)

        work_serializer = EmpWorkDetailsSerializer(work_instance)
        social_security_serializer = EmpSocialSecurityDetailsSerializer(social_security_instance)
        personal_serializer = EmpPersonalDetailsSerializer(personal_instance)
        insurance_serializer = EmpInsuranceDetailsSerializer(insurance_instance)
        salary_serializer    = EmpSalaryDetailsSerializer(salary_instance)

        response_data = {
            "work_details": work_serializer.data,
            "social_security_details": social_security_serializer.data,
            "personal_details": personal_serializer.data,
            "insurance_details": insurance_serializer.data,
            "salary_details": salary_serializer.data
        }
        return Response(response_data)
    
    permission_classes = [IsAuthenticated] 

    @action(detail=False, methods=['get'], url_path='retrieve_employee/(?P<user_id>\d+)')
    def retrieve_employee_deta(self, request, user_id=None):
        print("JELLO")

         # Ensure the user is authenticated and has a valid token
        if not request.user.is_authenticated:
            raise AuthenticationFailed("Invalid or expired token.")
        
        try:

            # Fetch the EmpWorkDetails for the given userId
            emp_work_details = EmpWorkDetails.objects.get(userId=user_id)

            # Fetch related details using the EmpWorkDetails instance
            social_security = EmpSocialSecurityDetails.objects.get(wdId=emp_work_details.wdId)
            personal_details = EmpPersonalDetails.objects.get(wdId=emp_work_details.wdId)
            insurance_details = EmpInsuranceDetails.objects.get(wdId=emp_work_details.wdId)
            salary_details = EmpSalaryDetails.objects.get(wdId=emp_work_details.wdId)

            # Serialize the data
            work_serializer = EmpWorkDetailsSerializer(emp_work_details)
            social_security_serializer = EmpSocialSecurityDetailsSerializer(social_security)
            personal_serializer = EmpPersonalDetailsSerializer(personal_details)
            insurance_serializer = EmpInsuranceDetailsSerializer(insurance_details)
            salary_serializer = EmpSalaryDetailsSerializer(salary_details)

            # Return the combined data as response
            return Response({
                'work_details': work_serializer.data,
                'social_security_details': social_security_serializer.data,
                'personal_details': personal_serializer.data,
                'insurance_details': insurance_serializer.data,
                'salary_details': salary_serializer.data
            })

        except EmpWorkDetails.DoesNotExist:
            return Response({"error": "Employee not found."}, status=404)

    permission_classes = [IsAuthenticated] 

    @transaction.atomic
    def partial_update(self, request, pk=None):
        self.check_permissions(request)
        
        # Fetch the main work details instance
        work_instance = get_object_or_404(EmpWorkDetails, pk=pk)

        # Extract data from request
        company_data = request.data.get('work_details', {})
        personal_data = request.data.get('personal_details', {})
        social_security_data = request.data.get('social_security_details', {})
        insurance_data = request.data.get('insurance_details', {})
        salary_data = request.data.get('salary_details', {})

        # Validate and update work details
        work_serializer = EmpWorkDetailsSerializer(work_instance, data=company_data, partial=True)
        if not work_serializer.is_valid():
            return Response({
                "message": "Validation errors occurred.",
                "work_details_errors": work_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        work_instance = work_serializer.save()

        # Initialize variables to track related instances
        personal_instance = None
        social_security_instance = None
        insurance_instance = None
        salary_instance = None

        # Update personal details
        if personal_data:
            try:
                personal_instance = EmpPersonalDetails.objects.get(wdId=work_instance)
                personal_serializer = EmpPersonalDetailsSerializer(personal_instance, data=personal_data, partial=False)
            except EmpPersonalDetails.DoesNotExist:
                personal_data['wdId'] = work_instance.pk
                personal_serializer = EmpPersonalDetailsSerializer(data=personal_data)

            if not personal_serializer.is_valid():
                return Response({
                    "message": "Validation errors occurred.",
                    "personal_details_errors": personal_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            personal_instance = personal_serializer.save()

        # Update social security details
        if social_security_data:
            try:
                social_security_instance = EmpSocialSecurityDetails.objects.get(wdId=work_instance)
                social_security_serializer = EmpSocialSecurityDetailsSerializer(social_security_instance, data=social_security_data, partial=False)
            except EmpSocialSecurityDetails.DoesNotExist:
                social_security_data['wdId'] = work_instance.pk
                social_security_serializer = EmpSocialSecurityDetailsSerializer(data=social_security_data)

            if not social_security_serializer.is_valid():
                return Response({
                    "message": "Validation errors occurred.",
                    "social_security_details_errors": social_security_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            social_security_instance = social_security_serializer.save()

        # Update insurance details
        if insurance_data:
            try:
                insurance_instance = EmpInsuranceDetails.objects.get(wdId=work_instance)
                insurance_serializer = EmpInsuranceDetailsSerializer(insurance_instance, data=insurance_data, partial=False)
            except EmpInsuranceDetails.DoesNotExist:
                insurance_data['wdId'] = work_instance.pk
                insurance_serializer = EmpInsuranceDetailsSerializer(data=insurance_data)

            if not insurance_serializer.is_valid():
                return Response({
                    "message": "Validation errors occurred.",
                    "insurance_details_errors": insurance_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            insurance_instance = insurance_serializer.save()

        # Update salary details
        if salary_data:
            try:
                salary_instance = EmpSalaryDetails.objects.get(wdId=work_instance)
                salary_serializer = EmpSalaryDetailsSerializer(salary_instance, data=salary_data, partial=False)
            except EmpSalaryDetails.DoesNotExist:
                salary_data['wdId'] = work_instance.pk
                salary_serializer = EmpSalaryDetailsSerializer(data=salary_data)

            if not salary_serializer.is_valid():
                return Response({
                    "message": "Validation errors occurred.",
                    "salary_details_errors": salary_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            salary_instance = salary_serializer.save()

        # Fetch the entire data for the wdId
        updated_work_instance = get_object_or_404(EmpWorkDetails, pk=work_instance.pk)
        work_details_serializer = EmpWorkDetailsSerializer(updated_work_instance)

        personal_instance = EmpPersonalDetails.objects.filter(wdId=work_instance).first()
        social_security_instance = EmpSocialSecurityDetails.objects.filter(wdId=work_instance).first()
        insurance_instance = EmpInsuranceDetails.objects.filter(wdId=work_instance).first()
        salary_instance = EmpSalaryDetails.objects.filter(wdId=work_instance).first()

        # Prepare the response with the updated data
        response_data = {
            "work_details": work_details_serializer.data,
            "personal_details": EmpPersonalDetailsSerializer(personal_instance).data if personal_instance else {},
            "social_security_details": EmpSocialSecurityDetailsSerializer(social_security_instance).data if social_security_instance else {},
            "insurance_details": EmpInsuranceDetailsSerializer(insurance_instance).data if insurance_instance else {},
            "salary_details": EmpSalaryDetailsSerializer(salary_instance).data if salary_instance else {}
        }

        return Response(response_data, status=status.HTTP_200_OK)

    permission_classes = [IsAuthenticated] 

    @transaction.atomic
    def destroy(self, request, pk=None):
        self.check_permissions(request)
        # Check if the work details exist
        work_instance = EmpWorkDetails.objects.filter(pk=pk).first()

        if not work_instance:
            return Response({
                "message": "Item not found."
            }, status=status.HTTP_404_NOT_FOUND)

        # If found, get related details and delete all
        social_security_instance = EmpSocialSecurityDetails.objects.filter(wdId=work_instance).first()
        personal_instance = EmpPersonalDetails.objects.filter(wdId=work_instance).first()
        insurance_instance = EmpInsuranceDetails.objects.filter(wdId=work_instance).first()
        salary_instance = EmpSalaryDetails.objects.filter(wdId=work_instance).first()

        if social_security_instance:
            social_security_instance.delete()
        if personal_instance:
            personal_instance.delete()
        if insurance_instance:
            insurance_instance.delete()
        if salary_instance:
            salary_instance.delete()
    
        work_instance.delete()

        return Response({
            "message": "Successfully deleted."
        }, status=status.HTTP_200_OK)

    permission_classes = [IsAuthenticated] 

    def list(self, request):
        # permission_classes = [IsAuthenticated]  

        self.check_permissions(request)

        # Get the company_id from the query parameters
        company_id = request.query_params.get('company_id', None)

        # Filter EmpWorkDetails by company_id
        if company_id:
            work_instances = EmpWorkDetails.objects.filter(company_id=company_id)
        else:
            # If company_id is not provided, return all work details
            work_instances = EmpWorkDetails.objects.all()

        # Initialize lists for serialized data
        work_details_list = []

        for work_instance in work_instances:
            # Serialize and add work details
            work_serializer = EmpWorkDetailsSerializer(work_instance)
            work_data = work_serializer.data

            # Retrieve related data
            social_security_instance = EmpSocialSecurityDetails.objects.filter(wdId=work_instance).first()
            personal_instance = EmpPersonalDetails.objects.filter(wdId=work_instance).first()
            insurance_instance = EmpInsuranceDetails.objects.filter(wdId=work_instance).first()
            salary_instance = EmpSalaryDetails.objects.filter(wdId=work_instance).first()

            # Serialize and add related details if they exist
            social_security_data = social_security_instance and EmpSocialSecurityDetailsSerializer(social_security_instance).data or {}
            personal_data = personal_instance and EmpPersonalDetailsSerializer(personal_instance).data or {}
            insurance_data = insurance_instance and EmpInsuranceDetailsSerializer(insurance_instance).data or {}
            salary_data = salary_instance and EmpSalaryDetailsSerializer(salary_instance).data or {}

            # Combine all details into one dictionary
            combined_data = {
                "work_details": work_data,
                "social_security_details": social_security_data,
                "personal_details": personal_data,
                "insurance_details": insurance_data,
                "salary_details": salary_data
            }

            # Add the combined data to the list
            work_details_list.append(combined_data)

        # Prepare the final response data
        response_data = {
            "employees": work_details_list
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    permission_classes = [IsAuthenticated] 

    @action(detail=False, methods=['get'], url_path='work-details')
    def list_custom_work_details(self, request):
        company_id = request.query_params.get('company_id', None)

        # Use select_related to optimize queries
        if company_id:
            work_instances = EmpWorkDetails.objects.filter(company_id=company_id)
        else:
            # If company_id is not provided, return all work details
            work_instances = EmpWorkDetails.objects.all()

        # Serialize the data
        serializer = CustomEmpWorkDetailsSerializer(work_instances, many=True)
        return Response({"custom_work_details": serializer.data}, status=status.HTTP_200_OK)


    # permission_classes = [IsAuthenticated] 

    # def retrieve(self, request, pk=None):
    #     """
    #     Retrieve details of a single employee based on their ID.
    #     """
    #     self.check_permissions(request)

    #     # Get the work instance by primary key
    #     work_instance = get_object_or_404(EmpWorkDetails, pk=pk)

    #     # Serialize the work details
    #     work_serializer = EmpWorkDetailsSerializer(work_instance)
    #     work_data = work_serializer.data

    #     # Retrieve related data
    #     social_security_instance = EmpSocialSecurityDetails.objects.filter(wdId=work_instance).first()
    #     personal_instance = EmpPersonalDetails.objects.filter(wdId=work_instance).first()
    #     insurance_instance = EmpInsuranceDetails.objects.filter(wdId=work_instance).first()
    #     salary_instance = EmpSalaryDetails.objects.filter(wdId=work_instance).first()

    #     # Serialize related details if they exist
    #     social_security_data = (
    #         EmpSocialSecurityDetailsSerializer(social_security_instance).data if social_security_instance else {}
    #     )
    #     personal_data = (
    #         EmpPersonalDetailsSerializer(personal_instance).data if personal_instance else {}
    #     )
    #     insurance_data = (
    #         EmpInsuranceDetailsSerializer(insurance_instance).data if insurance_instance else {}
    #     )
    #     salary_data = (
    #         EmpSalaryDetailsSerializer(salary_instance).data if salary_instance else {}
    #     )

    #     # Combine all details into one dictionary
    #     combined_data = {
    #         "work_details": work_data,
    #         "social_security_details": social_security_data,
    #         "personal_details": personal_data,
    #         "insurance_details": insurance_data,
    #         "salary_details": salary_data,
    #     }

    #     return Response(combined_data, status=status.HTTP_200_OK)
