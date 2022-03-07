import pytest

from rm_unneeded_f_str import visit_file


@pytest.mark.parametrize(
    'before, after', [
        ("f'hello world'", "'hello world'"),
        ("a = f'hello world'", "a = 'hello world'"),
        ("f'''hello world'''", "'''hello world'''"),

        # multi-line strings
        ("f'''hello\nworld'''", "'''hello\nworld'''"),
    ],
)
def test_removes_unneeded_import(before, after, tmp_path):
    file = tmp_path / 'a.py'
    file.write_text(before)

    visit_file(file)

    assert file.read_text() == after


@pytest.mark.parametrize(
    'unchanged_input', [
        "'hello world'",
        # multi-line strings
        "f'''hello\n{world}'''",

    ],
)
def test_doesnt_remove_unneeded_import(unchanged_input, tmp_path):
    file = tmp_path / 'a.py'
    file.write_text(unchanged_input)

    visit_file(file)

    assert file.read_text() == unchanged_input
