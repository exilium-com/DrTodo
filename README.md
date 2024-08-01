# DrToDo

[![Builds](https://github.com/exilium-com/DrTodo/actions/workflows/validate.yml/badge.svg)](https://github.com/exilium-com/DrTodo/actions/workflows/validate.yml)
[![Compatible Python Versions](https://img.shields.io/pypi/pyversions/drtodo?logo=python&logoColor=lightgray)](https://pypi.org/project/drtodo/)

[![Publish](https://github.com/exilium-com/DrTodo/actions/workflows/build.yml/badge.svg)](https://github.com/exilium-com/DrTodo/actions/workflows/build.yml)
[![Latest Github tag](https://img.shields.io/github/tag/exilium-com/DrTodo?logo=github&logoColor=lightgray&label=github%20tag)](https://github.com/exilium-com/DrTodo/tags/)
[![Published Version](https://img.shields.io/pypi/v/drtodo?logo=pypi&logoColor=lightgray&label=pypi%20tag)](https://pypi.org/project/drtodo/)
[![Commits since](https://img.shields.io/github/commits-since/exilium-com/drtodo/latest.svg?logo=github&logoColor=lightgray)](https://github.com/exilium-com/DrTodo/commits/main)

This is the internal README with build instructions, source code information etc.
The [external README with usage and installation instructions](READMEexample.md) is in the [drtodo folder](drtodo/). That is what is published in PyPI.org.

## Building

This now builds with `poetry`. Install poetry, then run `poetry install` in the root folder. It will install all
dependencies in a new environment and also the `todo` command. Run `todo --help` to test everything works.

### Installation

Must have [poetry](https://python-poetry.org/docs/#installation) installed in the system.
Then install the dependencies with `poetry install --no-root`.

### Building documents

Documents are built programmatically by doing two things, generating all man pages in raw MD format from DrToDo itself,
and generating detailed CLI options using [typer CLI](https://typer.tiangolo.com/typer-cli/#generate-docs).

This is done by [build.py](build.py) and the result is the [drtodo/README.md](drtodo/README.md) file. That file is
published to PyPI.org as the main README.

All documentation is available in the script itself with `todo man` or using the `--help` option with various commands.

You need to build docs manually with `poetry run python build.py` before you can build the drtodo with `poetry build`.

# Appendix: token format example

  ```python
tokens =
[
    {'type': 'paragraph', 'children': [{'type': 'text', 'raw': 'This is my cool project readme file.'}]},
    {'type': 'blank_line'},
    {
        'type': 'heading',
        'attrs': {'level': 1},
        'style': 'axt',
        'children': [{'type': 'text', 'raw': 'This is my MD file'}]
    },
    {'type': 'blank_line'},
    {'type': 'paragraph', 'children': [{'type': 'text', 'raw': 'Favorite ice cream flavors:'}]},
    {
        'type': 'list',
        'children': [
            {
                'type': 'list_item',
                'children': [{'type': 'block_text', 'children': [{'type': 'text', 'raw': 'Vanilla'}]}]
            },
            {
                'type': 'list_item',
                'children': [{'type': 'block_text', 'children': [{'type': 'text', 'raw': 'Peanut butter'}]}]
            },
            {
                'type': 'list_item',
                'children': [{'type': 'block_text', 'children': [{'type': 'text', 'raw': 'Chocolate'}]}]
            }
        ],
        'tight': True,
        'bullet': '-',
        'attrs': {'depth': 0, 'ordered': False}
    },
    {'type': 'heading', 'attrs': {'level': 2}, 'style': 'axt', 'children': [{'type': 'text', 'raw': 'TODO'}]},
    {'type': 'blank_line'},
    {
        'type': 'list',
        'children': [
            {
                'type': 'list_item',
                'children': [
                    {
                        'type': 'block_text',
                        'children': [{'type': 'text', 'raw': '['}, {'type': 'text', 'raw': 'x] write a readme'}]
                    }
                ],
                'attrs': {'checked': True, 'task_text': 'write a readme\n'},
                'task_item': {
                    'checked': True,
                    'text': 'write a readme\n',
                    'id': '56a01da3793c8fe2087a89a299d13bf977509f64',
                    'index': 0,
                    'token': ...,
                    'parent': ...
                }
            },
            {
                'type': 'list_item',
                'children': [
                    {
                        'type': 'block_text',
                        'children': [{'type': 'text', 'raw': '['}, {'type': 'text', 'raw': ' ] make it useful'}]
                    }
                ],
                'attrs': {'checked': False, 'task_text': 'make it useful\n'},
                'task_item': {
                    'checked': False,
                    'text': 'make it useful\n',
                    'id': '5869ea7816051ecdb5b9cce2d0fe09b365f9cc5b',
                    'index': 1,
                    'token': ...,
                    'parent': ...
                }
            }
        ],
        'tight': True,
        'bullet': '-',
        'attrs': {'depth': 0, 'ordered': False}
    },
    {
        'type': 'heading',
        'attrs': {'level': 2},
        'style': 'axt',
        'children': [{'type': 'text', 'raw': 'Bugs assigned to me'}]
    },
    {'type': 'blank_line'},
    {
        'type': 'list',
        'children': [
            {
                'type': 'list_item',
                'children': [
                    {
                        'type': 'block_text',
                        'children': [{'type': 'text', 'raw': '['}, {'type': 'text', 'raw': ' ] bug 1'}]
                    }
                ],
                'attrs': {'checked': False, 'task_text': 'bug 1\n'},
                'task_item': {
                    'checked': False,
                    'text': 'bug 1\n',
                    'id': '7a787ec3027b21b04a06ae2e3a89afaa05625175',
                    'index': 2,
                    'token': ...,
                    'parent': ...
                }
            },
            {
                'type': 'list_item',
                'children': [
                    {
                        'type': 'block_text',
                        'children': [{'type': 'text', 'raw': '['}, {'type': 'text', 'raw': ' ] bug 2'}]
                    }
                ],
                'attrs': {'checked': False, 'task_text': 'bug 2\n'},
                'task_item': {
                    'checked': False,
                    'text': 'bug 2\n',
                    'id': 'f237ece391025aecbf37c97aebe4ed5f16651577',
                    'index': 3,
                    'token': ...,
                    'parent': ...
                }
            }
        ],
        'tight': True,
        'bullet': '-',
        'attrs': {'depth': 0, 'ordered': False}
    }
]
```

# Command line options

```console
$ todo --help

 Usage: todo [OPTIONS] COMMAND [ARGS]...

 DrToDo, MD: a straightforward todo list manager for markdown files in git repos.

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --verbose             -v  --quiet  -q    Verbose or quiet output                                                        │
│                                          [default: verbose]                                                             │
│ --version             -V                 Show version and exit                                                          │
│ --install-completion                     Install completion for the current shell.                                      │
│ --show-completion                        Show completion for the current shell, to copy it or customize the             │
│                                          installation.                                                                  │
│ --help                                   Show this message and exit.                                                    │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Advanced options ──────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --global         -G  --local         -L        Force operation on global or local todo list. Default is chosen smartly: │
│                                                local if folder is under a git repo initialized for DrToDo, global       │
│                                                otherwise.                                                               │
│ --section                                TEXT  Section name in markdown file to use for todo list, with optional        │
│                                                heading level, e.g. '## TODO'                                            │
│ --done-section                           TEXT  Section name in markdown file to use for done items, with optional       │
│                                                heading level, e.g. '## DONE'                                            │
│ --reverse-order      --normal-order            Whether todo items should be in reverse order (latest first)             │
│                                                [default: normal-order]                                                  │
│ --mdfile                                 PATH  Markdown file to use for todo list                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ add     Add a new todo item to the list                                                                                 │
│ backup  Manage backups of markdown files                                                                                │
│ clean   Cleans up the todo list, removing all done items or moving them to a done section                               │
│ debug   List configuration, settings, version and other debug info. [or dbg]                                            │
│ done    Mark one or more todo items as done                                                                             │
│ init    Initialize DrToDo folder and files (in global location, use --local to override)                                │
│ list    List todo items in the list [or ls]                                                                             │
│ man     Show detailed help and context for settings, file format and heuristics                                         │
│ remove  Remove/delete todo items from the list [or rm]                                                                  │
│ show    Show markdown file(s) with rich rendering. Defaults to the active, configured files.                            │
│ undone  Mark one or more todo items as NOT done (undone)                                                                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

 DrToDo can manage items in a global todo list (typically in ~/.drtodo) and in a local todo list (if the current folder is
 under a git repo configured for DrToDo). Settings are read from config files and env variables (see todo man config).

 ```

