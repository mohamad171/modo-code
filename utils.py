import math
import random
import re

from django.contrib.auth.models import User
from django.db.models import F
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

class SuccessResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    data = serializers.JSONField()

class ErrorResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    message = serializers.CharField()

def arabic_to_persian(text: str) -> str:
    # arabic: persian
    characters = {
        'ك': 'ک',
        'دِ': 'د',
        'بِ': 'ب',
        'زِ': 'ز',
        'ذِ': 'ذ',
        'شِ': 'ش',
        'سِ': 'س',
        'ى': 'ی',
        'ي': 'ی',
        '١': '1',
        '٢': '2',
        '٣': '3',
        '٤': '4',
        '٥': '5',
        '٦': '6',
        '٧': '7',
        '٨': '8',
        '٩': '9',
        '٠': '0',
    }

    for arabic, persian in characters.items():
        text = text.replace(arabic, persian)

    return text

def generateOTP(lenght=8):
    digits = "0123456789"
    OTP = ""
    for i in range(lenght):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP


def error_response(message, code):
    return JsonResponse({"status": "failed", "message": f"{message}"}, status=code, safe=False)


def success_response(data):
    return JsonResponse({"status": "ok", "data": data}, status=200, safe=False)


def _multiple_replace(mapping, text):
    """
    Internal function for replace all mapping keys for a input string
    :param mapping: replacing mapping keys
    :param text: user input string
    :return: New string with converted mapping keys to values
    """
    pattern = "|".join(map(re.escape, mapping.keys()))
    return re.sub(pattern, lambda m: mapping[m.group()], str(text))


def convert_fa_numbers(input_str):
    """
    This function convert Persian numbers to English numbers.

    Keyword arguments:
    input_str -- It should be string

    Returns: English numbers
    """
    mapping = {
        '۰': '0',
        '۱': '1',
        '۲': '2',
        '۳': '3',
        '۴': '4',
        '۵': '5',
        '۶': '6',
        '۷': '7',
        '۸': '8',
        '۹': '9',
        '.': '.',
    }
    return _multiple_replace(mapping, input_str)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 200