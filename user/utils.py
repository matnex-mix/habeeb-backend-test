import csv
import io
import os
import bcrypt
import aiofiles
from rest_framework import serializers
import polars as pl
from itertools import islice
from .enums import RoleEnum
from common.exceptions import PermissionDeniedException

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Department, User, EligibleUserUpload
from django.conf import settings
from django.core.files.base import ContentFile


def hash_password(matric_number):
    """Hash the matric_number to use as a password."""
    # Generate a salt and hash the matric_number
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(matric_number.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def validate_eligible_student_upload(attrs, user: User, expected_headers):
    file = attrs['file']
    if not file.name.lower().endswith('.csv'):
        raise serializers.ValidationError({"file": "File must be a CSV file"})

    try:
        data_stream = pl.read_csv(file, dtypes={
            'Email': pl.Utf8,
            'First Name': pl.Utf8,
            'Last Name': pl.Utf8,
            'Middle Name': pl.Utf8,
            'Phone Number': pl.Utf8,
            'Matric Number': pl.Utf8,
            'Department Code': pl.Utf8,
        })

    except Exception as e:

        raise serializers.ValidationError({"file": f"Error reading CSV file: {str(e)}"})

    headers = set(data_stream.columns)
    row = data_stream.height

    if row < 1:
        raise serializers.ValidationError({"file": "File must not be empty"})

    if not expected_headers.issubset(headers):
        missing_headers = expected_headers - headers
        raise serializers.ValidationError(f"The CSV file is missing headers: {', '.join(missing_headers)}")

    special_characters = set('!@#$%^&*(){}[]|\\;:"\'<>,.?/~`')
    for header in headers:
        if any(char in special_characters for char in header):
            raise serializers.ValidationError(
                {"file": f"Header '{header}' contains special characters, which are not allowed."})

    return data_stream, row


ERROR_EMAIL_INVALID = "Email is not valid"
ERROR_EMAIL_DUPLICATE = "Email already exists"
ERROR_FIRST_NAME_EMPTY = "First name must not be empty"
ERROR_LAST_NAME_EMPTY = "Last name must not be empty"
ERROR_MIDDLE_NAME_EMPTY = "Middle name must not be empty"
ERROR_PHONE_INVALID = "Phone number is not valid"
ERROR_MATRIC_NUMBER_EMPTY = "Matric number must not be empty"
ERROR_MATRIC_NUMBER_EXISTS = "Matric number already exists"
ERROR_DEPARTMENT_CODE_INVALID = "Department code does not exist"
ERROR_PHONE_NUMBER_EXISTS = "Phone number already exists"


def validate_email_field(email, idx, errors_list):
    try:
        validate_email(email)
    except ValidationError:
        errors_list.append({"row": idx + 1, "column": "Email", "error": ERROR_EMAIL_INVALID, "value": email})
        return False
    if User.objects.filter(email=email).exists():
        errors_list.append({"row": idx + 1, "column": "Email", "error": ERROR_EMAIL_DUPLICATE, "value": email})
        return False
    return True


# Validate Department Code
def validate_department_code(department_code, idx, errors_list):
    department = Department.objects.filter(code=department_code).first()
    if not department:
        errors_list.append({"row": idx + 1, "column": "Department Code", "error": ERROR_DEPARTMENT_CODE_INVALID, "value": department_code
                            })
        return False, None
    return True, department


def validate_first_name(first_name, idx, errors_list):
    if not first_name or first_name.strip() == "":
        errors_list.append({"row": idx + 1, "column": "First Name", "error": ERROR_FIRST_NAME_EMPTY, "value": first_name
                            })
        return False
    return True


def validate_last_name(last_name, idx, errors_list):
    if not last_name or last_name.strip() == "":
        errors_list.append({"row": idx + 1, "column": "Last Name", "error": ERROR_LAST_NAME_EMPTY, "value": last_name
                            })
        return False
    return True


def validate_middle_name(middle_name, idx, errors_list):
    if not middle_name or middle_name.strip() == "":
        errors_list.append({"row": idx + 1, "column": "Last Name", "error": ERROR_MIDDLE_NAME_EMPTY, "value": middle_name
                            })
        return False
    return True


def validate_phone_number(phone_number, idx, errors_list):
    if not phone_number.isdigit():
        errors_list.append({"row": idx + 1, "column": "Phone Number", "error": ERROR_PHONE_INVALID, "value": phone_number
                            })
        return False
    if User.objects.filter(phone=phone_number).exists():
        errors_list.append(
            {"row": idx + 1, "column": "Phone Number", "error": ERROR_PHONE_NUMBER_EXISTS, "value": phone_number
             })
        return False
    return True


def validate_matric_number(matric_number, idx, errors_list):
    if not matric_number or matric_number.strip() == "":
        errors_list.append(
            {
                "row": idx + 1, "column": "Matric Number", "error": ERROR_MATRIC_NUMBER_EMPTY, "value": matric_number
            })
        return False
    if User.objects.filter(matric_no=matric_number).exists():
        errors_list.append(
            {
                "row": idx + 1, "column": "Matric Number", "error": ERROR_MATRIC_NUMBER_EXISTS, "value": matric_number
            })
        return False
    return True


def batch_generator(data_stream, batch_size):
    """Generator that yields successive batches from a data stream."""
    it = iter(data_stream)
    for first in it:
        yield [first] + list(islice(it, batch_size - 1))


def validate_file_upload_data(data_stream, file_upload: EligibleUserUpload, batch_size=100):
    """
    This function processes file uploads in batches, validates rows, writes errors to a CSV file,
    and returns an array of valid rows.
    """
    headers = ["Row", "Column", "Error", "Value"]
    errors_list = []
    valid_row_number = 0

    try:
        # Batch process the rows
        for batch_idx, batch in enumerate(batch_generator(data_stream.rows(named=True), batch_size), start=1):
            print(f"Processing batch {batch_idx}")

            for idx, row in enumerate(batch, start=(batch_idx - 1) * batch_size + 1):
                email = (row.get('Email') or '').strip()
                first_name = (row.get('First Name') or '').strip()
                last_name = (row.get('Last Name') or '').strip()
                middle_name = (row.get('Middle Name') or '').strip()
                phone_number = (row.get('Phone Number') or '').strip()
                matric_number = (row.get('Matric Number') or '').strip()
                department_code = (row.get('Department Code') or '').strip()

                # Validate fields
                is_error = False
                if not validate_email_field(email, idx, errors_list):
                    is_error = True

                if not validate_first_name(first_name, idx, errors_list):
                    is_error = True
                if not validate_last_name(last_name, idx, errors_list):
                    is_error = True
                if not validate_middle_name(middle_name, idx, errors_list):
                    is_error = True
                if not validate_phone_number(phone_number, idx, errors_list):
                    is_error = True
                if not validate_matric_number(matric_number, idx, errors_list):
                    is_error = True
                is_dept_valid, dept = validate_department_code(department_code, idx, errors_list)
                if not is_dept_valid and dept is None:
                    is_error = True

                # Only process and append valid rows
                if not is_error:
                    User.objects.create(email=email,
                                        firstname=first_name,
                                        lastname=last_name,
                                        middle_name=middle_name,
                                        phone=phone_number,
                                        department=dept,
                                        role=RoleEnum.Student.value,
                                        password=hash_password(matric_number),
                                        )

                    valid_row_number += 1

        # Prepare CSV content for errors
        file = None
        if errors_list:
            output = io.StringIO()
            writer = csv.writer(output)

            writer.writerow(headers)
            for error in errors_list:
                writer.writerow([
                    error["row"],
                    error["column"],
                    error["error"],
                    error["value"]
                ])

            # Save CSV file
            csv_content = output.getvalue()
            output.close()

            filename = f"batch_upload_error_file{file_upload.pk}.csv"
            file_path = os.path.join(settings.MEDIA_ROOT, filename)

            with open(file_path, 'w', newline='') as file:
                file.write(csv_content)

            file = ContentFile(csv_content, name=filename)

        # Return the file and array of valid rows
        return file, valid_row_number

    except Exception as e:
        print(f"Error during processing: {str(e)}")
        raise e
