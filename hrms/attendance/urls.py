from django.urls import path
from .views import TimesheetViewSet, upload_timesheet, SavePayData, PayCalculationViewSet, upload_attendance_file

urlpatterns = [
    path('save-pay-data/', SavePayData.as_view(), name='save-pay-data'),
    path('paycalculation/unique-months/', PayCalculationViewSet.as_view({'get': 'unique_months'}), name='unique-months'),
    path('paycalculation/by-month/', PayCalculationViewSet.as_view({'get': 'by_month'}), name='paycalculation-by-month'),
    path('upload-attendance/', upload_attendance_file, name='upload_attendance_file'),
    path('timesheet/upload/', upload_timesheet, name='upload_timesheet'),
    path('timesheet-view/<int:company_id>/<str:month>/', TimesheetViewSet.as_view({'get': 'list'}), name='timesheet-view'),

]
