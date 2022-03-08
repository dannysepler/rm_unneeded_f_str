rm_unneeded_f_str
=================

Find and replace unneeded f-strings in your code.


## Installation

`pip install rm_unneeded_f_str`

## Usage

Run via the CLI on a file or folder:
- `rm-unneeded-f-str path/to/file.py`
- `rm-unneeded-f-str path/to/folder/`

Or use as a pre-commit hook:

```yaml
-   repo: https://github.com/dannysepler/rm_unneeded_f_str
    rev: v0.1.0
    hooks:
    -   id: rm-unneeded-f-str
```

## Will replace

```diff
-f'hello world'
+'hello world'
-f'''hello world'''
+'''hello world'''
-rf'hello world'
+r'hello world'
-f'''hello
-world'''
+f'''hello
+world'''
```

## Will not replace

```python
f'hello {world}'
f'''hello
{world}'''
```
