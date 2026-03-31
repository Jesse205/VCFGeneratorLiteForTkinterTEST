from vcf_generator_lite.models.contact import MissingNumberError
from vcf_generator_lite.utils.locales import t


def get_localized_exception_msg(exception: BaseException):
    if isinstance(exception, MissingNumberError):
        return t("exception.missing_number")
    return str(exception)
