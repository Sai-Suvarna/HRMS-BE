from django.db import models
from company.models import CompanyDetails

class EmployeeCompensation(models.Model):
    ecId = models.AutoField(primary_key=True)  

    # Foreign key to CompanyDetails
    company = models.ForeignKey(CompanyDetails, on_delete=models.CASCADE, related_name="compensations")

    basic_percentage = models.FloatField() 
    hra_enabled = models.BooleanField(default=False)
    hra_percentage = models.FloatField(null=True, blank=True)    
    da_enabled = models.BooleanField(default=False)
    da_percentage = models.FloatField(null=True, blank=True)
    # Dynamic reimbursements stored as JSON
    reimbursements = models.JSONField(default=dict)  # Store key-value pairs for reimbursements

    advances = models.BooleanField(default=False)  
    variable_pay = models.BooleanField(default=False)  
    deductions = models.BooleanField(default=False)  
    quarterly_allowance = models.BooleanField(default=False)  
    quarterly_bonus = models.BooleanField(default=False)  
    annual_bonus = models.BooleanField(default=False)  
    special_allowances = models.BooleanField(default=False)  
    professional_tax = models.BooleanField(default=False)  
    
    esi = models.BooleanField(default=False) 
    pf = models.BooleanField(default=False)  
    pf_type = models.CharField(max_length=10, null=True, blank=True, choices=[
        ("!=15k", "No Limit for PF Deduction"),
        ("15k", "Wage limit 15k"),
        ("Both", "Both Options")
    ])  

    voluntary_pf = models.BooleanField(default=False, null=True)

    is_payroll_generated = models.BooleanField(default=False)

    def __str__(self):
        return f"Compensation for Employee"


