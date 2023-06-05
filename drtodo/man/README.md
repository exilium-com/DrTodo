# How to add new man pages

Simply create an md file in this folder, and format as usual. We do limited replacement of text
in the md file so you can use symbols in curly braces primarily for anything
in [Constants](../settings.py):
- {appname}
- {appdir}
- {version}
- {username}
- etc.

For more complex dynamic replacement implement a function in [man_command.py](../man_command.py)
see `md_config()` for an example.