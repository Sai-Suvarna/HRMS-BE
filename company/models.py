from django.db import models
# from accounts.models import AdminAccountManager
from accounts.models import Login

class CompanyDetails(models.Model):
    companyId = models.AutoField(primary_key=True)
    companyName = models.CharField(max_length=255)
    companyRegisteredId = models.CharField(max_length=255, unique=True)
    address = models.TextField()

    # Admin Details
    adminName = models.CharField(max_length=255)
    adminEmail = models.EmailField()
    adminPhoneNum = models.CharField(max_length=15)

    user = models.ForeignKey(Login, on_delete=models.CASCADE, null=True, blank=True)
    # Optional fields for additional data
    gst = models.CharField(max_length=15, blank=True, null=True)
    pan = models.CharField(max_length=10, blank=True, null=True)
    tan = models.CharField(max_length=10, blank=True, null=True)
    coi = models.ImageField(upload_to='coi/', blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    leavePolicy = models.FileField(upload_to='leave_policies/', blank=True, null=True)
    pfPolicy = models.FileField(upload_to='pf_policies/', blank=True, null=True)
    labourLawLicence = models.FileField(upload_to='labour_law_policies/', blank=True, null=True)

    # Setup progress flags
    isCompanyDetailsCompleted = models.BooleanField(default=False)
    payrollDone = models.BooleanField(default=False)
    employeeSetupDone = models.BooleanField(default=False)

    def __str__(self):
        return self.companyName

