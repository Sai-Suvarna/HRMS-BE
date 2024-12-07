from rest_framework import serializers
from .models import EmpWorkDetails, EmpSocialSecurityDetails, EmpPersonalDetails, EmpInsuranceDetails, EmpSalaryDetails
from company.models import CompanyDetails

class EmpSocialSecurityDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpSocialSecurityDetails
        fields = '__all__'

class EmpPersonalDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpPersonalDetails
        fields = '__all__'

class EmpInsuranceDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpInsuranceDetails
        fields = '__all__'

class EmpSalaryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpSalaryDetails
        fields = '__all__'

    def create(self, validated_data):
        reimbursements = validated_data.pop('reimbursements', {})
        salary_details = EmpSalaryDetails.objects.create(**validated_data)
        salary_details.reimbursements = reimbursements
        salary_details.save()
        return salary_details

class EmpWorkDetailsSerializer(serializers.ModelSerializer):

    social_security_details = serializers.PrimaryKeyRelatedField(queryset=EmpSocialSecurityDetails.objects.all(), required=False)
    personal_details = serializers.PrimaryKeyRelatedField(queryset=EmpPersonalDetails.objects.all(), required=False)
    insurance_details = serializers.PrimaryKeyRelatedField(queryset=EmpInsuranceDetails.objects.all(), required=False)
    salary_details = serializers.PrimaryKeyRelatedField(queryset=EmpSalaryDetails.objects.all(), required=False)
    company = serializers.PrimaryKeyRelatedField(read_only=True)  # Accepts company_id

    class Meta:
        model = EmpWorkDetails
        fields = '__all__'

    def create(self, validated_data):
        # Simply create the work details record
        return EmpWorkDetails.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Use default ModelSerializer update behavior for simplicity
        return super().update(instance, validated_data)
    

class CustomEmpSalaryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpSalaryDetails
        fields = ['wdId', 'CTCpayAMT', 'DLoansAMT', 'VPFAMT', 'reimbursements']


class CustomEmpWorkDetailsSerializer(serializers.ModelSerializer):
    salary_details = CustomEmpSalaryDetailsSerializer(source='empsalarydetails_set', many=True, read_only=True)

    class Meta:
        model = EmpWorkDetails
        fields = ['wdId', 'company', 'empId', 'firstName', 'lastName', 'roleType', 'salary_details']

