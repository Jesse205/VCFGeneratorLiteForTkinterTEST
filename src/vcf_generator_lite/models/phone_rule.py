import re
from dataclasses import dataclass


@dataclass
class PhoneRule:
    length: range | int
    regex: re.Pattern[str]

    def test(self, phone: str) -> bool:
        phone_length = len(phone)
        if (isinstance(self.length, int) and self.length != phone_length) or (
            isinstance(self.length, range) and phone_length not in self.length
        ):
            return False

        return self.regex.match(phone) is not None


DEFAULT_PHONE_RULES = [
    # 11 位中国大陆手机号
    PhoneRule(length=11, regex=re.compile(r"^1[3456789]\d{9}$")),
]
