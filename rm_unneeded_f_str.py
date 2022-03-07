from __future__ import annotations

import argparse
import ast
from pathlib import Path


class JoinedStrVisitor(ast.NodeVisitor):
    """An f-string is a type of joined string"""

    def __init__(self) -> None:
        self.unneeded_f_strings: list[ast.JoinedStr] = []

    def visit_JoinedStr(self, node: ast.JoinedStr):
        if not any(isinstance(v, ast.FormattedValue) for v in node.values):
            self.unneeded_f_strings.append(node)


def remove_unneeded_f_strings(
    contents: str, *, visitor: JoinedStrVisitor,
) -> str:
    content_list = contents.splitlines()
    for unneeded_f_string in visitor.unneeded_f_strings:
        # ASTs start at line 1, but we expect our lists to start at 0
        line_no = unneeded_f_string.lineno - 1
        loc = unneeded_f_string.col_offset
        content_list[line_no] = content_list[line_no][:loc] + \
            content_list[line_no][loc + 1:]
    return '\n'.join(content_list)

def visit_file(file: Path) -> bool:
    contents = file.read_text()
    visitor = JoinedStrVisitor()
    visitor.visit(ast.parse(contents))

    if not visitor.unneeded_f_strings:
        return False
    else:
        print(f'Rewriting {str(file)}')
        new_contents = remove_unneeded_f_strings(contents, visitor=visitor)
        if contents.endswith('\n') and not new_contents.endswith('\n'):
            new_contents += '\n'
        file.write_text(new_contents)
        return True


def visit_path(file_or_dir: str) -> None:
    path = Path(file_or_dir)
    if path.is_dir():
        for p in path.glob('**/*.py'):
            visit_file(p)
    else:
        visit_file(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('file_or_dir')
    args = parser.parse_args()

    visit_path(args.file_or_dir)


if __name__ == '__main__':
    main()
