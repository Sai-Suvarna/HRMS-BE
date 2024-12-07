from rest_framework import serializers
from .models import EmployeeCompensation
import json

class EmployeeCompensationSerializer(serializers.ModelSerializer):
    reimbursements = serializers.JSONField()
    class Meta:
        model = EmployeeCompensation
        fields = '__all__'

    def to_representation(self, instance):
        # Ensure that reimbursements is returned as a dictionary, even if stored as a string
        data = super().to_representation(instance)
        if isinstance(instance.reimbursements, str):
            data['reimbursements'] = json.loads(instance.reimbursements)
        return data

    def create(self, validated_data):
        reimbursements = validated_data.pop('reimbursements', {})
        
        # Create the EmployeeCompensation instance
        employee_compensation = EmployeeCompensation.objects.create(**validated_data)
        
        # Store reimbursements as a JSON field
        employee_compensation.reimbursements = reimbursements
        employee_compensation.save()
        
        return employee_compensation
