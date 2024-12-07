from rest_framework import serializers
from .models import TimeSheet

class TimesheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSheet
        fields = ['empId', 'company', 'name', 'month', 'no_of_days', 'attendance', 'lop_days', 'OT', 'allowance', 'deductions']


from .models import PayCalculation

class PayCalculationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayCalculation
        fields = '__all__'  # Include all fields from the model
