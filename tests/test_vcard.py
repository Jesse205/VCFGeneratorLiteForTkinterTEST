from concurrent.futures import ThreadPoolExecutor, wait
from io import StringIO

from vcf_generator_lite.util.vcard import VCardFileGenerator

area_tag = "-----"

input_content = f"""
李四\t13445467890
王五\t13554678907
赵六\t13645436748
{area_tag}
孙七\t1234567890
周八\t"13789012345"
吴九\t13 789012345
郑十\t1389012345a
"""

input_list = input_content.split("\n")
input_valid_until = input_list.index(area_tag)


def test_vcard_file_generator():
    progress_history: list[tuple[float, bool]] = []
    result_io = StringIO()
    with ThreadPoolExecutor(max_workers=1) as executor:
        generator = VCardFileGenerator(executor)
        generator.add_progress_callback(lambda progress, determinate: progress_history.append((progress, determinate)))
        generate_future = generator.start(input_content, result_io)
        wait([generate_future])
    generate_result = generate_future.result()
    result_list = [item for item in result_io.getvalue().split("\n\n") if item != ""]

    assert generate_result.exceptions == [], "不应有任何异常"

    for item in generate_result.invalid_items:
        assert item.row_position >= input_valid_until, f"第 {input_valid_until} 行前不应解析错误"
        assert item.content == input_list[item.row_position], f"第 {item.row_position} 行数据不匹配"

    assert progress_history[-1][0] == 1.0, "末尾进度应该为 1.0"

    for result_item in result_list:
        assert result_item.startswith("BEGIN:VCARD\n"), "VCard 应以 BEGIN:VCARD 开头"
        assert result_item.endswith("\nEND:VCARD"), "VCard 应以 END:VCARD 结尾"
