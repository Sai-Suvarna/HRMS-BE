from django.db import models
from company.models import CompanyDetails
from payrole.models import EmployeeCompensation
from django.utils import timezone
from dateutil.relativedelta import relativedelta
# from accounts.models import Employee
from accounts.models import Login
# Employee Work Details
class EmpWorkDetails(models.Model):
    wdId = models.AutoField(primary_key=True)  

    # Foreign Key to CompanyDetails
    company = models.ForeignKey(CompanyDetails, on_delete=models.CASCADE, related_name="employees",null=True, blank=True)

    # Employee-specific fields
    empId = models.CharField(max_length=255, unique=True)  
    firstName = models.CharField(max_length=100)  
    lastName = models.CharField(max_length=100)  
    employmentStatus = models.CharField(max_length=100)  
    employmentType = models.CharField(max_length=100)
    companyEmailId = models.EmailField(null=True, blank=True)  
    group = models.CharField(max_length=100, null=True, blank=True)  
    department = models.CharField(max_length=100,null=True, blank=True)  
    roleType = models.CharField(max_length=100,null=True, blank=True) 
    currentRole = models.CharField(max_length=100)  
    reportingManager = models.CharField(max_length=100) 
    dateOfJoining = models.DateField(null=True, blank=True, default=None)
    dateOfRelieving = models.DateField(null=True, blank=True, default=None)  
    reasonForLeaving = models.TextField(null=True, blank=True)  
    monthYearOfTermination = models.CharField(max_length=100, null=True, blank=True)
    totalExpInThisCompany = models.CharField(max_length=100, null=True, blank=True)
    totalExpBeforeJoining = models.CharField(max_length=100, null=True, blank=True)
    totalExperience = models.CharField(max_length=100, null=True, blank=True)
    previousDateOfJoining = models.DateField(null=True, blank=True, default=None)
    previousEmployer = models.CharField(max_length=100, null=True, blank=True)
    userId = models.OneToOneField(Login, null=True, blank=True, on_delete=models.SET_NULL, related_name="employeesrole") 

    def save(self, *args, **kwargs):
        if self.dateOfJoining:
            today = timezone.now().date() 
            print("TODAY:",today)
            experience = relativedelta(today, self.dateOfJoining)
            print("Exp:",experience)

            years_in_company = experience.years
            print("YR:",years_in_company)
            months_in_company = experience.months
            print("MON:",months_in_company)
            self.totalExpInThisCompany = f"{years_in_company} yr {months_in_company} mon"

            if self.totalExpBeforeJoining:
                try:
                    parts = self.totalExpBeforeJoining.split(' ')
                    total_exp_years = int(parts[0])
                    total_exp_months = int(parts[2])
                except (ValueError, IndexError):
                    total_exp_years, total_exp_months = 0, 0
            else:
                total_exp_years, total_exp_months = 0, 0

            totalExperience = relativedelta(years=total_exp_years, months=total_exp_months)
            totalExperience += experience

            years_total_exp = totalExperience.years
            months_total_exp = totalExperience.months
            self.totalExperience = f"{years_total_exp} yr {months_total_exp} mon"

        super(EmpWorkDetails, self).save(*args, **kwargs)
    
# Employee Social Security Details
class EmpSocialSecurityDetails(models.Model):
    ssdId = models.AutoField(primary_key=True)
    wdId = models.ForeignKey(EmpWorkDetails, on_delete=models.CASCADE)
    panNum = models.CharField(max_length=20,null=True, blank=True)
    uanNum = models.CharField(max_length=20,null=True, blank=True)
    aadharNum = models.CharField(max_length=20,null=True, blank=True)
    bankName = models.CharField(max_length=100,null=True, blank=True)
    ifscCode = models.CharField(max_length=20,null=True, blank=True)
    bankAccountNumber = models.CharField(max_length=50,null=True, blank=True)

    def __str__(self):
        return f"Social Security Details for {self.wdId.empId}"


# Employee Personal Details
class EmpPersonalDetails(models.Model):
    pdId = models.AutoField(primary_key=True)
    wdId = models.ForeignKey(EmpWorkDetails, on_delete=models.CASCADE)
    personalEmailId = models.EmailField(null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=50)
    educationalQualification = models.CharField(max_length=100, null=True, blank=True)
    maritalStatus = models.CharField(max_length=50)
    marriageDate = models.DateField(null=True, blank=True)
    currentAddress = models.TextField()
    permanentAddress = models.TextField()
    generalContact = models.TextField(null=True, blank=True)
    emergencyContact = models.TextField(null=True, blank=True)
    relationship = models.CharField(max_length=100, null=True, blank=True)
    relationshipName = models.CharField(max_length=100, null=True, blank=True)
    bloodGroup = models.CharField(max_length=10, null=True, blank=True)
    shirtSize = models.CharField(max_length=10, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return f"Personal Details for {self.wdId.empId}"


# Employee Insurance Details
class EmpInsuranceDetails(models.Model):
    isdId = models.AutoField(primary_key=True)
    wdId = models.ForeignKey(EmpWorkDetails, on_delete=models.CASCADE)
    fathersName = models.CharField(max_length=100, null=True, blank=True)
    fathersDOB = models.DateField(null=True, blank=True)
    mothersName = models.CharField(max_length=100, null=True, blank=True)
    mothersDOB = models.DateField(null=True, blank=True)
    spouseName = models.CharField(max_length=100, null=True, blank=True)
    spouseDOB = models.DateField(null=True, blank=True)
    child1 = models.CharField(max_length=100, null=True, blank=True)
    child1DOB = models.DateField(null=True, blank=True)
    child2 = models.CharField(max_length=100, null=True, blank=True)
    child2DOB = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Insurance Details for {self.wdId.empId}"

# Employee Salary Details
class EmpSalaryDetails(models.Model):
    sdId = models.AutoField(primary_key=True)  # Primary key for the salary details

    # Foreign Key to EmpWorkDetails
    wdId = models.ForeignKey(EmpWorkDetails, on_delete=models.CASCADE)

    # Salary components, reflecting the company's compensation structure
    CTCpayAMT = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Cost to Company (CTC)
    BasicpayAMT = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Basic pay
    DApayAMT = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    HRApayAMT = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # House Rent Allowance (HRA)
    AdvancesAMT = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Advances, if any
    VariableAMT = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Variable pay
    QAllowanceAMT = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Quarterly Allowance
    QBonusAMT = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Quarterly Bonus
    ABonusAMT = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Annual Bonus
    SAllowancesAMT = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Special Allowances
    PTAMT = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Professional Tax
    PFAMT = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Provident Fund Amount (PF)
    ESIAMT = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Employee State Insurance (ESI)
    DLoansAMT = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Deducted Loans, if any
    VPFAMT = models.DecimalField(max_digits=10, decimal_places=2, default=0) # Voluntary PF 
    # Dynamic reimbursements stored as JSON
    reimbursements = models.JSONField(default=dict)  # Store key-value pairs for reimbursements
    pf_type = models.CharField(max_length=10, null=True, blank=True, choices=[
        ("!=15k", "No Limit for PF Deduction"),
        ("15k", "Wage limit 15k")
    ])

    def __str__(self):
        return f"Salary Details for Employee: {self.wdId.empId}"