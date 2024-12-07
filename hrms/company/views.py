from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CompanyDetails  
from .serializers import CompanyDetailsSerializer, CompanyDetailsGetSerializer
# from accounts.models import AdminAccountManager
from accounts.models import Login
from django.shortcuts import get_object_or_404

class CompanyDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Get the user_id from the request user (derived from the access token)
        user_id = request.user.id  # Assumes request.user is populated with the correct user ID from the token
        print("USER ID",user_id)
        # Retrieve the user instance from the User model
        user = get_object_or_404(Login, id=user_id)

        # Serialize and validate the incoming data
        serializer = CompanyDetailsSerializer(data=request.data)
        if serializer.is_valid():
            # Save the new company instance with the retrieved user
            company = serializer.save(user=user)

            # Mark company setup as complete
            company.isCompanyDetailsCompleted = True
            company.save()

            # Return response with companyId
            return Response({
                "message": "Successfully submitted",
                "companyId": company.companyId  # Include companyId in the response
            }, status=status.HTTP_201_CREATED)
        
        # If validation fails, return bad request
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompanyDetailsGetView(APIView):

    permission_classes = [IsAuthenticated] 

    def get(self, request, *args, **kwargs):
        user_id = request.user.id  # Assumes request.user is populated with the correct user ID from the token
        print("USER ID",user_id)
        # Retrieve the user instance from the User model
        user = get_object_or_404(Login, id=user_id)

        # Retrieve the company details for the authenticated user
        company_details = CompanyDetails.objects.filter(user=user)

        if company_details.exists():
            # Serialize the company details
            serializer = CompanyDetailsGetSerializer(company_details, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No company details found for the user"}, status=status.HTTP_404_NOT_FOUND) 


class CompanyDetailRetrieveView(APIView):

    permission_classes = [IsAuthenticated] 

    def get(self, request, companyId):
        try:
            # Fetch the company using companyId
            company = CompanyDetails.objects.get(companyId=companyId)
            serializer = CompanyDetailsGetSerializer(company)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CompanyDetails.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateCompanyDetailsView(APIView):
    permission_classes = [IsAuthenticated]  

    def put(self, request, companyId):
        try:
            company = CompanyDetails.objects.get(companyId=companyId)
            serializer = CompanyDetailsSerializer(company, data=request.data, partial=True)  # Use partial=True for partial updates

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CompanyDetails.DoesNotExist:
            return Response({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)