import re
from typing import NamedTuple, Optional

CHINA_PHONE_PATTERN = re.compile(r"^1[356789]\d{9}$")


class Contact(NamedTuple):
    name: str
    phone: str
    note: Optional[str] = None


def is_china_mobile_phone(phone: str) -> bool:
    return len(phone) == 11 and CHINA_PHONE_PATTERN.match(phone) is not None


def parse_contact(person_text: str):
    parts = person_text.split()
    if len(parts) < 2:
        raise ValueError(f"The person info is illegal: '{person_text}'.")

    for i, part in enumerate(parts):
        if is_china_mobile_phone(part):
            phone = part
            name = " ".join(parts[:i])
            note_parts = parts[i + 1:]
            note = " ".join(note_parts) if note_parts else None
            break
    else:
        raise ValueError(f"The person info is illegal: '{person_text}'.")

    return Contact(name, phone, note)
