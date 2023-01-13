from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path


class JoinedStrVisitor(ast.NodeVisitor):
    """An f-string is a type of joined string"""

    def __init__(self) -> None:
        self.unneeded_f_strings: list[ast.JoinedStr] = []

    def visit_JoinedStr(self, node: ast.JoinedStr):
        if not any(isinstance(v, ast.FormattedValue) for v in node.values):
            self.unneeded_f_strings.append(node)


def _no_ws(s: str) -> str:
    """ strip all whitespace from a string """
    return ''.join(s.split())


def remove_unneeded_f_strings(
    contents: str, *, visitor: JoinedStrVisitor,
) -> str:
    content_list = contents.splitlines()
    for unneeded_f_string in visitor.unneeded_f_strings:
        loc = unneeded_f_string.col_offset

        # This is likely a bug in python https://bugs.python.org/issue16806
        if sys.version_info[:2] == (3, 7) and loc == -1:
            continue

        # ASTs start at line 1, but we expect our lists to start at 0
        line_no = unneeded_f_string.lineno - 1

        if sys.version_info[:2] == (3, 7):
            end_line_no = line_no
        else:
            end_line_no = unneeded_f_string.end_lineno
            end_line_no = line_no if end_line_no is None else end_line_no - 1

        # in case a string like rf'hello' exists
        if content_list[line_no][loc] == 'r':
            loc += 1

        # A safety check, we should never remove a character that's not 'f'
        # This can occur during the following line of python code, for example:
        #
        # a = 'hi' f'hello'
        #
        # unfortunately, python combines this ^ into one Constant in the AST
        if content_list[line_no][loc] != 'f':
            continue

        content_list[line_no] = content_list[line_no][:loc] + \
            content_list[line_no][loc + 1:]

        # Handle escaped curly braces. For example: f'{{ }}' -> '{ }'
        for i in range(line_no, end_line_no + 1):
            line = content_list[i]
            if '{{' in line or '}}' in line:
                content_list[i] = line.replace('{{', '{').replace('}}', '}')

    return '\n'.join(content_list)


def visit_file(file: Path) -> bool:
    contents = file.read_text()
    visitor = JoinedStrVisitor()

    try:
        parsed = ast.parse(contents)
    except SyntaxError:
        print(f'Skipping {str(file)} due to its syntax errors')
        return False

    visitor.visit(parsed)

    if not visitor.unneeded_f_strings:
        return False
    else:
        new_contents = remove_unneeded_f_strings(contents, visitor=visitor)
        if _no_ws(contents) == _no_ws(new_contents):
            # If no whitespace change occurs, we probably skipped it.
            # Therefore, mark as unchanged
            return False
        else:
            print(f'Rewriting {str(file)}')
            if contents.endswith('\n') and not new_contents.endswith('\n'):
                new_contents += '\n'
            file.write_text(new_contents)
            return True


def visit_paths(files_or_dirs: list[str]) -> int:
    ret = 0
    for file_or_dir in files_or_dirs:
        path = Path(file_or_dir)
        if path.is_dir():
            for p in path.glob('**/*.py'):
                ret += int(visit_file(p))
        else:
            ret += int(visit_file(path))
    return ret


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('files_or_dirs', nargs='*')
    args = parser.parse_args()

    return visit_paths(args.files_or_dirs)


if __name__ == '__main__':
    main()
