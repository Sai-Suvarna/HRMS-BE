from django.urls import path
from .views import RegisterAdminAccountManager, RegisterEmployee, LoginView,  GetCompanyIdView , CompanyStatusView, GetUserNameView
from rest_framework_simplejwt.views import TokenRefreshView,     TokenObtainPairView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/admin/', RegisterAdminAccountManager.as_view(), name='register_admin'),
    path('register/employee/', RegisterEmployee.as_view(), name='register_employee'),
    path('login/', LoginView.as_view(), name='login'),
    path('company-status/<int:user_id>/', CompanyStatusView.as_view(), name='company-status'),
    path('companyid/<int:user_id>/', GetCompanyIdView.as_view(), name='get_company_id'),
    path('username/<int:user_id>/', GetUserNameView.as_view(), name='get_username'),


]
