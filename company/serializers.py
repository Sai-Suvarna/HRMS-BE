from rest_framework import serializers
from .models import CompanyDetails
from django.conf import settings

class CompanyDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDetails
        fields = [
            'companyName', 'companyRegisteredId', 'address', 
            'adminName', 'adminEmail', 'adminPhoneNum', 
            'gst', 'pan', 'tan', 'logo', 'coi',
            'leavePolicy', 'pfPolicy', 'labourLawLicence'
        ]

class CompanyStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDetails
        fields = ['isCompanyDetailsCompleted', 'payrollDone', 'employeeSetupDone']  # Fixed field names

    def update(self, instance, validated_data):
        instance.isCompanyDetailsCompleted = validated_data.get('isCompanyDetailsCompleted', instance.isCompanyDetailsCompleted)
        instance.payrollDone = validated_data.get('payrollDone', instance.payrollDone)
        instance.employeeSetupDone = validated_data.get('employeeSetupDone', instance.employeeSetupDone)
        instance.save()
        return instance



class CompanyDetailsGetSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    coi_url = serializers.SerializerMethodField()
    leave_policy_url = serializers.SerializerMethodField()
    pf_policy_url = serializers.SerializerMethodField()
    labour_law_licence_url = serializers.SerializerMethodField()

    class Meta:
        model = CompanyDetails
        fields = [
            'companyName', 'companyRegisteredId', 'address', 
            'adminName', 'adminEmail', 'adminPhoneNum', 
            'gst', 'pan', 'tan', 'logo_url', 'coi_url',
            'leave_policy_url', 'pf_policy_url', 'labour_law_licence_url'
        ]
    def get_logo_url(self, obj):
        return self.build_file_url(obj.logo)

    def get_coi_url(self, obj):
        return self.build_file_url(obj.coi)

    def get_leave_policy_url(self, obj):
        return self.build_file_url(obj.leavePolicy)

    def get_pf_policy_url(self, obj):
        return self.build_file_url(obj.pfPolicy)

    def get_labour_law_licence_url(self, obj):
        return self.build_file_url(obj.labourLawLicence)

    def build_file_url(self, file_path):
        if file_path:
            return f"{settings.MEDIA_URL}{file_path}"
        return None
   