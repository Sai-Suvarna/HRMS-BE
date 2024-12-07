from django.urls import path
from .views import EmployeeCompensationAPI, PayrollSettingsView

urlpatterns = [
    path('employee-compensation/', EmployeeCompensationAPI.as_view(), name='employee-compensation-list-create'),
    # path('employee-compensation/<int:pk>/', EmployeeCompensationAPI.as_view(), name='employee-compensation-detail'),
    path('payroll-settings/<int:company_id>/', PayrollSettingsView.as_view(), name='payroll-settings'),

]
