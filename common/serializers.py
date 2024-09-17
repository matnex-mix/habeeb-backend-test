import base64
import six

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.files.base import ContentFile
from drf_extra_fields.fields import Base64FileField

from rest_framework import serializers

from .validator import PasswordComplexityValidator, validate_alpha, validate_name


class EnumCharField(serializers.CharField):
    def __init__(self, enum_class, *args, **kwargs):
        self.enum_class = enum_class
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        if value is not None:
            return str(value)
        return None

    def to_internal_value(self, data):
        if data is not None:
            try:
                return getattr(self.enum_class, data)
            except AttributeError:
                raise serializers.ValidationError(f"Invalid enum value: {data}")
        return None


class CustomPasswordField(serializers.CharField):
    def __init__(self, *args, **kwargs):
        self.validators.append(PasswordComplexityValidator())
        super().__init__(*args, **kwargs)

    def run_validators(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages)


class AlphabetOnlySerializer(serializers.CharField):
    def __init__(self, *args, **kwargs):
        # Add the custom validator to the field
        self.validators.append(validate_alpha)
        super().__init__(*args, **kwargs)


class CustomNameFieldSerializer(serializers.CharField):
    def __init__(self, *args, **kwargs):
        self.validators.append(validate_name)
        super().__init__(*args, **kwargs)


class EmptySerializer(serializers.Serializer):
    pass


class DigitOnlyFieldSerializer(serializers.CharField):
    def to_internal_value(self, data):
        if not str(data).isdigit():
            raise serializers.ValidationError("This field should contain digits only.")
        return data


class AnyBase64FileField(Base64FileField):
    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError('Expected a dictionary with "file" and "filename" keys.')

        if 'file' not in data or 'filename' not in data:
            raise serializers.ValidationError('Both "file" and "filename" keys are required.')

        file_data = data['file']
        filename = data['filename']

        # Ensure file_data is a string and appears to be base64 encoded
        if not isinstance(file_data, six.string_types):
            raise serializers.ValidationError('File data must be a base64 encoded string.')

        if 'data:' in file_data and ';base64,' in file_data:
            header, file_data = file_data.split(';base64,')

        try:
            decoded_file = base64.b64decode(file_data, validate=True)
        except (base64.binascii.Error, ValueError):
            raise serializers.ValidationError('Invalid base64 format.')

        complete_file_name = filename
        return ContentFile(decoded_file, name=complete_file_name)
