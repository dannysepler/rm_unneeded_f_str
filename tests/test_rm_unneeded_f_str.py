import sys

import pytest

from rm_unneeded_f_str import visit_file


@pytest.mark.parametrize(
    'before, after', [
        ("f'hello'", "'hello'"),
        ("a = f'hello'", "a = 'hello'"),
        ("f'''hello'''", "'''hello'''"),
        ("rf'hello'", "r'hello'"),
        ("fr'hello'", "r'hello'"),

        # preserves leading and trailing whitespace
        ("f'hello'\n", "'hello'\n"),
        ("\nf'hello'\n", "\n'hello'\n"),
    ],
)
def test_removes_unneeded_f_str(before, after, tmp_path):
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
        ("fr'''hello\nworld'''", "r'''hello\nworld'''"),
        ("rf'''hello\nworld'''", "r'''hello\nworld'''"),
    ],
)
def test_removes_unneeded_f_str_on_multilines(before, after, tmp_path):
    file = tmp_path / 'a.py'
    file.write_text(before)

    ret = visit_file(file)

    assert file.read_text() == after
    assert ret is True


@pytest.mark.parametrize(
    'unchanged_input', [
        "'hello'",
        # multi-line strings
        "f'''hello\n{world}'''",
        # we can't rewrite the following since the AST combines
        # it into one string. At the very least, let's not fail
        "{'a': 'hi' f'hello'}",
    ],
)
def test_doesnt_remove_needed_f_str(unchanged_input, tmp_path):
    file = tmp_path / 'a.py'
    file.write_text(unchanged_input)

    ret = visit_file(file)

    assert file.read_text() == unchanged_input
    assert ret is False


@pytest.mark.parametrize(
    'before, after', [
        # These braces need to be deduplicated
        ("f'{{ hello }}'", "'{ hello }'"),
        ("f'''hello\n{{world}}'''", "'''hello\n{world}'''"),
        ("f'{{ yes }}'\n'{{ no }}'", "'{ yes }'\n'{{ no }}'"),
        # This brace is actually useful, no rewriting should occur
        ("f'{{{ hello }}}'", "f'{{{ hello }}}'"),
    ],
)
def test_removes_escaped_brace(tmp_path, before, after):
    file = tmp_path / 'a.py'
    file.write_text(before)

    visit_file(file)

    assert file.read_text() == after


def test_skips_file_with_syntax_errors(tmp_path, capsys):
    file = tmp_path / 'a.py'
    file.write_text("print 'hello'")

    ret = visit_file(file)

    captured = capsys.readouterr()
    assert f'Skipping {str(file)} due to its syntax errors' in captured.out
    assert ret is False
