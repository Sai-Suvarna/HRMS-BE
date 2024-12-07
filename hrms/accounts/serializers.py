from rest_framework import serializers
from .models import Login

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Login
        fields = [
            'id', 'userName', 'email', 'password', 'phoneNum',
            'company', 'role', 'is_company_setup_complete',
            'is_payroll_setup_complete', 'created_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        return Login.objects.create_user(**validated_data)
