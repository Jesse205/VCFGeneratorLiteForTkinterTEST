from vcf_generator_lite.models.contact import PhoneNotFoundError
from vcf_generator_lite.utils.locales import t


def get_localized_exception_msg(exception: BaseException):
    if isinstance(exception, PhoneNotFoundError):
        return t("exception.phone_not_found")
    return str(exception)
