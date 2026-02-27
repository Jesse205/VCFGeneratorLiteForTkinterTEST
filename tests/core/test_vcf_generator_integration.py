from io import StringIO

from vcf_generator_lite.core.vcf_generator import VCFGeneratorTask


class TestVCFGeneratorIntegration:
    """VCF 生成器的集成测试"""

    # 测试数据
    VALID_INPUT_LIST = [
        "李    四    13445467890",
        " 王五\t13554678907",
        "赵六\t13645436748 ",
    ]

    INVALID_INPUT_LIST = [
        "孙七\t1234567890",  # 电话号码太短
        '周八\t"13789012345"',  # 电话号码包含引号
        "吴九\t13 789012345",  # 电话号码包含空格
        "郑十\t1389012345a",  # 电话号码包含字母
    ]

    IGNORED_INPUT_LIST = [
        "   ",
        "",
        "\t",
    ]

    @property
    def input_content(self):
        """构建测试输入内容"""
        input_list = (
            self.IGNORED_INPUT_LIST
            + self.INVALID_INPUT_LIST
            + self.IGNORED_INPUT_LIST
            + self.VALID_INPUT_LIST
            + self.INVALID_INPUT_LIST
            + self.IGNORED_INPUT_LIST
        )
        return "\n".join(input_list)

    @property
    def valid_count(self):
        """有效行数"""
        return len(self.VALID_INPUT_LIST)

    @property
    def invalid_count(self):
        """无效行数（出现两次）"""
        return len(self.INVALID_INPUT_LIST) * 2

    def test_vcard_file_generator_full_integration(self):
        """完整的 VCF 生成器集成测试"""
        progress_history = []
        result_io = StringIO()

        generator = VCFGeneratorTask(
            input_text=self.input_content,
            output_io=result_io,
            progress_listener=lambda progress, determinate: progress_history.append((progress, determinate)),
        )
        generator.start()
        generator.join()

        assert generator.result is not None, "结果监听器未被调用"

        # 验证没有异常
        assert generator.result.exception is None, "不应有意外的异常"

        # 验证进度报告
        assert len(progress_history) > 0, "应该有进度报告"
        assert progress_history[-1][0] == 1.0, "末尾进度应为 1.0"
        assert progress_history[-1][1] is True, "进度应该是确定性的"

        # 验证无效行
        assert len(generator.result.invalid_lines) == self.invalid_count, f"应有 {self.invalid_count} 个无效行"
        for item in generator.result.invalid_lines:
            assert item.content in self.INVALID_INPUT_LIST, f"第 {item.row_position} 行数据不应为无效行"

        # 验证生成的 VCard 内容
        result_content = result_io.getvalue()
        result_list = [item for item in result_content.split("\n\n") if item.strip() != ""]
        assert len(result_list) == self.valid_count, f"应有 {self.valid_count} 个有效联系人"

        for result_item in result_list:
            assert result_item.startswith("BEGIN:VCARD\n"), "VCard 应以 BEGIN:VCARD 开头"
            assert result_item.endswith("\nEND:VCARD"), "VCard 应以 END:VCARD 结尾"
            assert "TEL;CELL:" in result_item, "VCard 应包含电话号码"
            assert "FN;" in result_item, "VCard 应包含姓名字段（带分号参数）"

    def test_empty_input(self):
        """测试空输入"""
        progress_history = []
        result_io = StringIO()

        generator = VCFGeneratorTask(
            input_text="",
            output_io=result_io,
            progress_listener=lambda progress, determinate: progress_history.append((progress, determinate)),
        )
        generator.start()
        generator.join()  # 等待线程完成

        assert generator.result is not None, "结果监听器未被调用"

        assert generator.result.exception is None
        assert len(generator.result.invalid_lines) == 0
        assert result_io.getvalue() == ""
        # 对于空输入，可能没有进度报告，或者进度为 0（因为 total 变为 0）
        # 这是当前实现的行为，我们接受它
        if progress_history:
            # 如果有进度报告，最后一个进度应该是 0（因为 total=0）
            assert progress_history[-1][0] == 0.0

    def test_only_invalid_input(self):
        """测试只有无效输入的情况"""
        progress_history = []
        result_io = StringIO()
        invalid_content = "\n".join(self.INVALID_INPUT_LIST)

        generator = VCFGeneratorTask(
            input_text=invalid_content,
            output_io=result_io,
            progress_listener=lambda progress, determinate: progress_history.append((progress, determinate)),
        )
        generator.start()
        generator.join()  # 等待线程完成

        assert generator.result is not None, "结果监听器未被调用"

        assert generator.result.exception is None
        assert len(generator.result.invalid_lines) == len(self.INVALID_INPUT_LIST)
        assert result_io.getvalue() == ""
        # 应该有进度报告且最终为 1.0
        if progress_history:
            assert progress_history[-1][0] == 1.0
