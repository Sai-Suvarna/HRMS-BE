from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .models import TimeSheet, EmpWorkDetails, CompanyDetails, PayCalculation
from .serializers import PayCalculationSerializer
from .serializers import TimesheetSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import pandas as pd
import re
import calendar
import os

@csrf_exempt
def upload_attendance_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        file_path = default_storage.save(file.name, ContentFile(file.read()))
        absolute_path = os.path.join(default_storage.location, file_path)

        try:
            # Load and process the CSV file
            data = pd.read_csv(absolute_path, header=None)
            data = data.dropna(how='all', axis=1)  # Drop empty columns
            data.dropna(how='all', inplace=True)  # Drop empty rows

            date_range_text = data.iloc[1, 1]
            match = re.search(r"([A-Za-z]+)\s+\d{1,2}\s+(\d{4})", date_range_text)
            if match:
                month_name, year = match.groups()
                formatted_month = f"{month_name} {year}"
                month_number = list(calendar.month_abbr).index(month_name)
                days_in_month = calendar.monthrange(int(year), month_number)[1]
            else:
                formatted_month = "Unknown"
                days_in_month = 0

            structured_data = []
            current_department = None
            current_empcode = None
            current_empname = None

            for i, row in data.iterrows():
                row_data = row.dropna().values
                if any("Department:" in str(cell) for cell in row_data):
                    current_department = next((cell for cell in row_data if "Department:" not in str(cell)), None)
                elif any("Emp. Code:" in str(cell) for cell in row_data):
                    try:
                        emp_code_index = next(idx for idx, cell in enumerate(row_data) if "Emp. Code:" in str(cell))
                        emp_name_index = next(idx for idx, cell in enumerate(row_data) if "Emp. Name:" in str(cell))
                        current_empcode = row_data[emp_code_index + 1]
                        current_empname = row_data[emp_name_index + 1]
                    except (IndexError, StopIteration):
                        continue
                elif any("Status" == str(cell) for cell in row_data) and current_empcode and current_empname:
                    attendance = row_data[1:]
                    structured_data.append({
                        'Department': current_department,
                        'Emp ID': current_empcode,
                        'Name': current_empname,
                        'attendance': attendance,
                        'Month': formatted_month,
                        'No. of Days': days_in_month
                    })
                    current_empcode = None
                    current_empname = None

            attendance_df = pd.DataFrame(structured_data)

            def calculate_attendance_metrics(attendance_list):
                present_days = list(attendance_list).count('P')
                absent_days = list(attendance_list).count('A')
                WO_days = list(attendance_list).count('WO')
                WOP_days = list(attendance_list).count('WOP')
                return present_days, absent_days, WO_days, WOP_days

            if 'attendance' in attendance_df.columns:
                attendance_df[['present_days', 'LOP Days', 'WO_days', 'WOP_days']] = attendance_df['attendance'].apply(
                    lambda x: pd.Series(calculate_attendance_metrics(x))
                )

            attendance_df['S NO'] = range(1, len(attendance_df) + 1)
            attendance_df['Attendance'] = attendance_df['present_days'] + attendance_df['WO_days'] + attendance_df['WOP_days']
            attendance_summary = attendance_df[['S NO', 'Department', 'Emp ID', 'Name', 'Month', 'No. of Days', 'Attendance', 'LOP Days', 'present_days', 'WO_days', 'WOP_days']]

            # Save the processed file to the media directory
            output_file_name = 'attendance_summary.xlsx'
            output_file_path = os.path.join(default_storage.location, output_file_name)
            attendance_summary.to_excel(output_file_path, index=False)

            # Generate a public URL for the processed file
            public_file_url = f"{settings.MEDIA_URL}{output_file_name}"
            full_url = request.build_absolute_uri(public_file_url)

            return JsonResponse({'message': 'File processed successfully!', 'downloadUrl': full_url})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

class TimesheetViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated] 
    def list(self, request, company_id, month):
        print(f"Received request to fetch timesheets for company ID: {company_id} and month: {month}")

        # Filter timesheets by company ID and month
        timesheets = TimeSheet.objects.filter(company_id=company_id, month=month)
        print(f"Filtered Timesheets Queryset: {timesheets}")

        if not timesheets:
            return Response(
                {"message": f"No timesheets found for company ID: {company_id} and month: {month}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TimesheetSerializer(timesheets, many=True)
        return Response({"Attendance_data": serializer.data}, status=status.HTTP_200_OK)

permission_classes = [IsAuthenticated] 
@api_view(['POST'])
def upload_timesheet(request):
    try:
        # Assuming the request data is a list of dictionaries
        data = request.data  
        for entry in data:
            # Check if empId exists in the entry, and handle the case where it's missing or empty
            empId = entry.get('empId', None)
            company_id = entry.get('company')
            if empId and company_id:
                # Fetch the employee object
                employee = EmpWorkDetails.objects.get(empId=empId)
                
                # Fetch the company object using company_id
                company = CompanyDetails.objects.get(companyId=company_id)

                # Create the TimeSheet entry
                TimeSheet.objects.create(
                    empId=employee,
                    company=company,
                    name=entry['name'],
                    month=entry['month'],
                    no_of_days=entry['noOfDays'],
                    attendance=entry['attendance'],
                    lop_days=entry['lopDays'],
                    OT=entry['OT'],
                    allowance=entry['allowance'],
                    deductions=entry['deductions']
                )
            else:
                # Handle cases where empId is missing, you can skip or log it
                print(f"Skipping entry with missing empId: {entry}")

        return JsonResponse({"status": "success", "message": "Timesheet uploaded successfully"})
    except KeyError as e:
        return JsonResponse({"status": "error", "message": f"Missing key: {str(e)}"}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

class SavePayData(APIView):
    permission_classes = [IsAuthenticated] 
    def post(self, request):
        serializer = PayCalculationSerializer(data=request.data)  

        if serializer.is_valid():
            serializer.save()  # Save the data if valid
            return Response({"message": "Data saved successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from .models import PayCalculation
from .serializers import PayCalculationSerializer

class PayCalculationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated] 
    @action(detail=False, methods=['get'])
    def unique_months(self, request):
        unique_months = PayCalculation.objects.values_list('month', flat=True).distinct()
        return Response(list(unique_months), status=status.HTTP_200_OK)
    
    permission_classes = [IsAuthenticated] 
    @action(detail=False, methods=['get'])
    def by_month(self, request):
        month = request.query_params.get('month')
        company_id = request.query_params.get('company_id')
        
        if month and company_id:
            queryset = PayCalculation.objects.filter(month=month, company_id=company_id)
            serializer = PayCalculationSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"error": "Month and company_id parameters are required"},
            status=status.HTTP_400_BAD_REQUEST
        )
