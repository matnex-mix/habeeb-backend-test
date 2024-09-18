import asyncio
import threading
from rest_framework import serializers
from common.serializers import AnyBase64FileField
from user.models import EligibleUserUpload
from user.utils import validate_eligible_student_upload
from user.tasks import handle_file_upload
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from common.helper import run_async


class EligibleUserUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    data_stream = None

    class Meta:
        model = EligibleUserUpload
        fields = [
            'file',
        ]

    def validate(self, attrs):
        user = self.context['request'].user
        expected_headers = {"Email", "First Name", "Last Name", "Middle Name", "Phone Number", "Matric Number",
                            "Department Code"}

        attrs['created_by'] = user

        data_stream, total_upload = validate_eligible_student_upload(attrs, user, expected_headers)
        attrs['total_upload'] = total_upload
        self.data_stream = data_stream

        return attrs

    @transaction.atomic()
    def create(self, validated_data):
        user = self.context['request'].user
        data = validated_data.copy()
        file_upload = super().create(validated_data)
        data['data_stream'] = self.data_stream
        handle_file_upload(data['data_stream'], file_upload, user)

        return file_upload


class ListUserSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(max_length=100)

    class Meta:
        model = get_user_model()
        fields = ['firstname', 'lastname', 'email', 'phone', "matric_no", "department_name", "middle_name"]


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for user authentication object"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        if email:
            user = authenticate(
                request=self.context.get('request'),
                username=email.lower().strip(),
                password=password
            )

            if not user:
                msg = _('Unable to authenticate with provided credentials')
                raise serializers.ValidationError(msg, code='authentication')
            attrs['user'] = user
        return attrs


class CustomObtainTokenPairSerializer(TokenObtainPairSerializer):
    pass
