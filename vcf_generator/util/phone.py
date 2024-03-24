import re

CHINA_PHONE_PATTERN = re.compile(r"1[356789]\d{9}")


def is_china_phone(phone: str) -> bool:
    return CHINA_PHONE_PATTERN.match(phone) is not None
