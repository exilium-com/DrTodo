lli# DrToDo

[![Python Validated](https://github.com/exilium-com/DrTodo/actions/workflows/validate.yml/badge.svg)](https://github.com/exilium-com/DrTodo/actions/workflows/validate.yml)

This is the internal README with build instructions, source code information etc.
The [external README with usage and installation instructions](drtodo/README.md) is in the [drtodo folder](drtodo/). That is what is published in PyPI.org.

This is a sample list of TODOs locally tracked in this git repo.

To Do (used for testing):
- [x] @WarpedPixel this is ~~to be~~ done
- [ ] to do by 2/3/23 #32

## Building

This now builds with `poetry`. Install poetry, then run `poetry install` in the root folder. It will install all
dependencies in a new environment and also the `todo` command. Run `todo --help` to test everything works.

## Building documents

We can build detailed documents mostly programmatically by doing two things, generating all man pages in raw MD format from DrToDo itself, and generating detailed CLI options using [typer CLI](https://typer.tiangolo.com/typer-cli/#generate-docs)

```console
$ todo man --raw all > manpages.md
$ poetry run typer drtodo.main utils docs --name DrToDo --output clihelp.md
$ cat manpages.md clihelp.md > drtodo/README_NEW.md
```

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

 DrTodo, MD: a straightforward todo list manager for markdown files in git repos.

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion        [bash|zsh|fish|powershell|pwsh]  Install completion for the       │
│                                                              specified shell.                 │
│                                                              [default: None]                  │
│ --show-completion           [bash|zsh|fish|powershell|pwsh]  Show completion for the          │
│                                                              specified shell, to copy it or   │
│                                                              customize the installation.      │
│                                                              [default: None]                  │
│ --help                                                       Show this message and exit.      │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Global Options ──────────────────────────────────────────────────────────────────────────────╮
│ --settings  -s      PATH  Settings file to use                                                │
│                           [default: ~/.drtodo]                                       │
│ --verbose   -v            Verbose output                                                      │
│                           [default: True]                                                     │
│ --version   -V            Show version and exit                                               │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ File Selection Options ──────────────────────────────────────────────────────────────────────╮
│ --mdfile                             PATH  Markdown file to use for todo list                 │
│                                            [default: TEST.md]                                 │
│ --section                            TEXT  Section name in markdown file to use for todo      │
│                                            list, with optional heading level, e.g. '## TODO'  │
│ --reverse-order    --normal-order          Whether todo items should be in reverse order      │
│                                            (latest first)                                     │
│                                            [default: normal-order]                            │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────╮
│ add     Add a new todo item to the list                                                       │
│ debug   List configuration, settings, version and other debug info. [or dbg]                  │
│ done    Mark one or more todo items as done                                                   │
│ init    Initialize DrTodo folder and files                                                    │
│ list    List todo items in the list [or ls]                                                   │
│ man     Show detailed help and context for settings, file format and heuristics               │
│ undone  Mark one or more todo items as NOT done (undone)                                      │
╰───────────────────────────────────────────────────────────────────────────────────────────────╯

 DrTodo can manage items in a global todo list (~/.drtodo/TEST.md) and in a local todo list
 (~/work/src/DrTodo/TEST.md). Settings are read from config files and env variables (see todo
 man config).

 ```

