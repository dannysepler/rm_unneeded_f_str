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
    rev: v0.2.0
    hooks:
    -   id: rm-unneeded-f-str
```

## Will replace

```diff
-f'hello'
+'hello'
-f'''hello'''
+'''hello'''
-rf'hello'
+r'hello'
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
