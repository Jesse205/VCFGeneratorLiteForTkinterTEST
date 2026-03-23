from typing import NamedTuple

from vcf_generator_lite.models.phone_rule import DEFAULT_PHONE_RULES, PhoneRule


class Contact(NamedTuple):
    phone: str
    name: str | None = None
    note: str | None = None


class PhoneNotFoundError(ValueError):
    def __init__(self) -> None:
        super().__init__("Phone not found")


def _get_phone_index(contact_parts: list[str], rules: list[PhoneRule]) -> int:
    for i, part in enumerate(contact_parts):
        if len(part) > 0 and any((rule.test(part)) for rule in rules):
            return i
    raise PhoneNotFoundError()


def parse_contact(contact_text: str, rules: list[PhoneRule] | None = None, delimiter: str | None = None) -> Contact:
    if rules is None:
        rules = DEFAULT_PHONE_RULES

    if delimiter is not None:
        parts = contact_text.split(delimiter)
        parts = [part.strip() for part in parts if part.strip()]
    else:
        # 结果不会包含空字符串，并且字符串两侧也没有空白字符。
        # 详见：https://docs.python.org/zh-cn/3.14/library/stdtypes.html#str.split
        parts = contact_text.split()

    phone_index = _get_phone_index(parts, rules)

    phone = parts[phone_index]
    name = " ".join(parts[:phone_index]) if phone_index > 0 else None
    note = " ".join(parts[phone_index + 1 :]) if phone_index < len(parts) - 1 else None

    return Contact(
        phone=phone,
        name=name,
        note=note,
    )
