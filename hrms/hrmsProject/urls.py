from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from employee.views import CombinedDetailsViewSet

# Create a router and register the employee viewset
router = DefaultRouter()
router.register(r'employee', CombinedDetailsViewSet, basename='employee-details')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include('accounts.urls')),
    path('api/', include('company.urls')),
    path('api/', include('payrole.urls')),
    path('api/', include('attendance.urls')),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
