import re
import polars as pl
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from rest_framework import serializers


class PasswordComplexityValidator:
    """
    Validates whether the password meets the following criteria:
    - Contains at least 8 characters.
    - Contains at least one uppercase letter.
    - Contains at least one digit.
    - Contains at least one special character.
    """

    # Regular expressions for the validation checks
    min_length = 8
    uppercase_pattern = r'[A-Z]'
    digit_pattern = r'\d'
    special_char_pattern = r'[!@#$%^&*(),.?":{}|<>]'

    def validate(self, password, user=None):
        # Check for minimum length
        if len(password) < self.min_length:
            raise ValidationError(
                _("Password must contain at least %(min_length)d characters.") % {'min_length': self.min_length},
                code='password_too_short'
            )

        # Check for at least one uppercase letter
        if not re.search(self.uppercase_pattern, password):
            raise ValidationError(
                _("Password must contain at least one uppercase letter."),
                code='password_no_upper'
            )

        # Check for at least one digit
        if not re.search(self.digit_pattern, password):
            raise ValidationError(
                _("Password must contain at least one digit."),
                code='password_no_digit'
            )

        # Check for at least one special character
        if not re.search(self.special_char_pattern, password):
            raise ValidationError(
                _("Password must contain at least one special character."),
                code='password_no_special'
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least %(min_length)d characters, one uppercase letter,"
            " one digit, and one special character."
        ) % {'min_length': self.min_length}


def validate_alpha(value):
    if not re.match(r'^[a-zA-Z]+$', value):
        raise ValidationError(
            _('This field should contain only alphabets.'),
            code='invalid_name'
        )


def validate_name(value):
    if re.match(r'^[^a-zA-Z]+$', value):
        raise ValidationError(_('This field must contain at least one alphabet character.'), code='invalid_name')


def validate_account_number(value):
    if not re.match(r'^[0-9]+$', value):
        raise ValidationError(_('This field must contain only digits.'), code='invalid_account_number')
    if len(value) != 10:
        raise ValidationError(_('This field must contain at least 10 characters.'), code='invalid_account_number')
