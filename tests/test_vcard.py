from concurrent.futures import ThreadPoolExecutor, wait
from io import StringIO

from vcf_generator_lite.services.vcf_generator import VCFGeneratorTask

area_tag = "-----"

valid_input_list = [
    "李    四    13445467890",
    " 王五\t13554678907",
    "赵六\t13645436748 ",
]
invalid_input_list = [
    "孙七\t1234567890",
    '周八\t"13789012345"',
    "吴九\t13 789012345",
    "郑十\t1389012345a",
]
ignored_input_list = [
    "   ",
    "",
    "\t",
]

input_list = (
    ignored_input_list
    + invalid_input_list
    + ignored_input_list
    + valid_input_list
    + invalid_input_list
    + ignored_input_list
)
input_content = "\n".join(input_list)

valid_count = len(valid_input_list)
invalid_count = len(invalid_input_list) * 2


def test_vcard_file_generator():
    progress_history: list[tuple[float, bool]] = []
    result_io = StringIO()
    with ThreadPoolExecutor(max_workers=1) as executor:
        generator = VCFGeneratorTask(
            executor=executor,
            progress_listener=lambda progress, determinate: progress_history.append((progress, determinate)),
            input_text=input_content,
            output_io=result_io,
        )
        generate_future = generator.start()
        wait([generate_future])
    generate_result = generate_future.result()

    assert generate_result.exceptions == [], "不应有任何异常"
    assert progress_history[-1][0] == 1.0, "末尾进度应为 1.0"

    for item in generate_result.invalid_lines:
        assert item.content in invalid_input_list, f"第 {item.row_position} 行数据不应为无效行"
        assert item.content == input_list[item.row_position], f"第 {item.row_position} 行数据不匹配"
    assert len(generate_result.invalid_lines) == invalid_count, f"应有 {invalid_count} 个无效行"

    result_list = [item for item in result_io.getvalue().split("\n\n") if item != ""]
    assert len(result_list) == valid_count, f"应有 {valid_count} 个有效行"
    for result_item in result_list:
        assert result_item.startswith("BEGIN:VCARD\n"), "VCard 应以 BEGIN:VCARD 开头"
        assert result_item.endswith("\nEND:VCARD"), "VCard 应以 END:VCARD 结尾"
