import sys

import pytest

from rm_unneeded_f_str import visit_file


@pytest.mark.parametrize(
    'before, after', [
        ("f'hello world'", "'hello world'"),
        ("a = f'hello world'", "a = 'hello world'"),
        ("f'''hello world'''", "'''hello world'''"),

        # preserves trailing new-line if available
        ("f'hello world'\n", "'hello world'\n"),
    ],
)
def test_removes_unneeded_import(before, after, tmp_path):
    file = tmp_path / 'a.py'
    file.write_text(before)

    visit_file(file)

    assert file.read_text() == after


# TODO: When py3.7 is deprecated, add this to the above test
@pytest.mark.skipif(
    sys.version_info[:2] == (3, 7),
    reason='py3.7 skips this behavior',
)
@pytest.mark.parametrize(
    'before, after', [
        ("f'''hello\nworld'''", "'''hello\nworld'''"),
    ],
)
def test_removes_unneeded_import_on_multilines(before, after, tmp_path):
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


def test_skips_file_with_syntax_errors(tmp_path, capsys):
    file = tmp_path / 'a.py'
    file.write_text("print 'hello world'")

    visit_file(file)

    captured = capsys.readouterr()
    assert f'Skipping {str(file)} due to its syntax errors' in captured.out
