from django.urls import path
from company.views import CompanyDetailsView , CompanyDetailsGetView , CompanyDetailRetrieveView, UpdateCompanyDetailsView

urlpatterns = [
    path('companydetails/', CompanyDetailsView.as_view(), name='companydetails'),
    path('companydetails/retrieve/<int:companyId>/', CompanyDetailRetrieveView.as_view(), name='retrieve-company-details'),
    path('getcompanydetails/', CompanyDetailsGetView.as_view(), name='retrieve-company-details'),

    path('companydetails/update/<int:companyId>/', UpdateCompanyDetailsView.as_view(), name='update-company-details'),  # New endpoint for updating

]


