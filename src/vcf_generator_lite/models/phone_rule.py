import re
from dataclasses import dataclass


@dataclass
class PhoneRule:
    length_max: int
    length_min: int
    regex: re.Pattern[str]

    def test(self, phone: str) -> bool:
        if not (self.length_min <= len(phone) <= self.length_max):
            return False
        if not self.regex.match(phone):
            return False
        return True


DEFAULT_PHONE_RULES = [
    # 11 位中国大陆手机号
    PhoneRule(length_max=11, length_min=11, regex=re.compile(r"^1[3456789]\d{9}$")),
]
