import pytest

from vcf_generator_lite.models.contact import Contact, PhoneNotFoundError, parse_contact

FAKE_PHONES = [
    "18445522522",
    "13421322443",
    "16524812629",
    "18724657441",
    "15928176628",
    "15801124810",
    "17111469035",
    "13428242703",
    "13297276916",
    "15331568900",
]


class TestParseContact:
    # 正常情况测试
    def test_with_note(self):
        """测试包含备注的联系人信息"""
        result = parse_contact("张三 18445522522 工程师")
        assert result == Contact(phone="18445522522", name="张三", note="工程师")

    def test_without_note(self):
        """测试无备注的联系人信息"""
        result = parse_contact("张三 18445522522")
        assert result == Contact(phone="18445522522", name="张三")

    def test_whitout_name(self):
        """测试姓名为空的情况"""
        result = parse_contact("18445522522 工程师")
        assert result == Contact(phone="18445522522", note="工程师")

    def test_whitout_name_and_not(self):
        """测试姓名和备注都为空的情况"""
        result = parse_contact("18445522522")
        assert result == Contact(phone="18445522522")

    def test_name_with_spaces(self):
        """测试姓名包含空格的情况"""
        result = parse_contact("张    三 丰 18445522522   工程师")
        assert result == Contact(phone="18445522522", name="张 三 丰", note="工程师")

    def test_multiple_phones(self):
        """测试包含多个手机号的情况（应使用第一个有效手机号）"""
        result = parse_contact("张三 18445522522 13421322443 备用号码")
        assert result == Contact(phone="18445522522", name="张三", note="13421322443 备用号码")

    def test_tabs_to_spaces(self):
        """测试使用制表符转空格"""
        result = parse_contact("张三\t18445522522 工\t程\t师")
        assert result == Contact(phone="18445522522", name="张三", note="工 程 师")

    # 异常情况测试
    def test_missing_valid_phone(self):
        """测试缺少有效手机号的情况"""
        with pytest.raises(PhoneNotFoundError):
            parse_contact("张三 1844 工程师")

    def test_missing_phone(self):
        """测试缺失电话号码的情况"""
        with pytest.raises(PhoneNotFoundError):
            parse_contact("张三")
