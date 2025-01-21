from dataclasses import dataclass

from vcf_generator_lite.util.phone import is_china_phone


@dataclass
class Person:
    name: str
    phone: int


def parse_person(person_text: str):
    info_list: list[str] = person_text.rsplit(" ", 1)
    if len(info_list) != 2:
        raise ValueError(f"The person info is illegal: '{person_text}'.")
    name, phone = info_list
    if not name:
        raise ValueError(f"The name is illegal: '{name}'.")
    if not phone.isnumeric() or not is_china_phone(phone):
        raise ValueError(f"The phone number is illegal: '{phone}'.")
    return Person(name, int(phone))
