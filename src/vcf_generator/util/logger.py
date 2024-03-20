TAG_INFO = "\033[30m[INFO]\033[0m"
TAG_ERROR = "\033[31m[ERROR]\033[0m"
TAG_WARNING = "\033[33m[WARNING]\033[0m"


def error(*values: object):
    """
    使用固定的格式打印错误日志。
    :param values: 信息列表
    """
    print(TAG_ERROR, *values)


def warning(*values: object):
    """
    使用固定的格式打印警告日志。
    :param values: 信息列表
    """
    print(TAG_WARNING, *values)


def info(*values: object):
    """
    使用固定的格式打印信息日志。
    :param values: 信息列表
    """
    print(TAG_INFO, *values)
