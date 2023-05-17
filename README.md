# DrToDo

[![Python Validated](https://github.com/exilium-com/DrTodo/actions/workflows/validate.yml/badge.svg)](https://github.com/exilium-com/DrTodo/actions/workflows/validate.yml)


This is a sample list of TODOs locally tracked in this git repo.

To Do:
- [x] @WarpedPixel this is ~~to be~~ done
- [ ] to do by 2/3/23 #32
- [ ] @WarpedPixel Implement add item write. Look at item list token will point to token in the parsed
  stream and then we add after it (or before).


## Building

This now builds with `poetry`. Install poetry, then run `poetry install` in the root folder. It will install all
dependencies in a new environment and also the `todo` command. Run `todo --help` to test everything works.

# Appendix: token format example

  ```python
tokens =
[
    {'type': 'paragraph', 'children': [{'type': 'text', 'raw': 'This is my cool project readme file.'}]},
    {'type': 'blank_line'},
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
                    'id': '01bd483d62ed72acfc9ca46c93242d5bf45979de',
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
                    'id': 'e046af4d0e84752a3bf1dd9dc74d5cb453b2f5b0',
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
    {'type': 'heading', 'attrs': {'level': 2}, 'style': 'axt', 'children': [{'type': 'text', 'raw': 'Bugs assigned to me'}]},
    {'type': 'blank_line'},
    {
        'type': 'list',
        'children': [
            {
                'type': 'list_item',
                'children': [
                    {'type': 'block_text', 'children': [{'type': 'text', 'raw': '['}, {'type': 'text', 'raw': ' ] bug 1'}]}
                ],
                'attrs': {'checked': False, 'task_text': 'bug 1\n'},
                'task_item': {
                    'checked': False,
                    'text': 'bug 1\n',
                    'id': 'cadea03965ec665c41b0336412d3cbf3624b58db',
                    'index': 2,
                    'token': ...,
                    'parent': ...
                }
            },
            {
                'type': 'list_item',
                'children': [
                    {'type': 'block_text', 'children': [{'type': 'text', 'raw': '['}, {'type': 'text', 'raw': ' ] bug 2'}]}
                ],
                'attrs': {'checked': False, 'task_text': 'bug 2\n'},
                'task_item': {
                    'checked': False,
                    'text': 'bug 2\n',
                    'id': 'a69434ae372dca71a54f3ed1a6ec444723fb42d7',
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

 Usage: python -m todo [OPTIONS] COMMAND [ARGS]...

 DrTodo, MD: a straightforward todo list manager for markdown files in git repos.

╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion        [bash|zsh|fish|powershell|pwsh]  Install completion for the specified │
│                                                              shell.                               │
│                                                              [default: None]                      │
│ --show-completion           [bash|zsh|fish|powershell|pwsh]  Show completion for the specified    │
│                                                              shell, to copy it or customize the   │
│                                                              installation.                        │
│                                                              [default: None]                      │
│ --help                                                       Show this message and exit.          │
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Global Options ──────────────────────────────────────────────────────────────────────────────────╮
│ --settings  -s      PATH  Settings file to use                                                    │
│                           [default: /Users/bcs/.drtodo]                                           │
│ --verbose   -v            Verbose output                                                          │
│ --version   -V            Show version and exit                                                   │
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ File Selection Options ──────────────────────────────────────────────────────────────────────────╮
│ --mdfile        PATH  Markdown file to use for todo list                                          │
│                       [default: TODO.md]                                                          │
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────────────────╮
│ add     Add a new todo item to the list                                                           │
│ debug   List configuration, settings, version and other debug info.                               │
│ done    Mark one or more todo items as done                                                       │
│ init    Initialize DrTodo folder and files                                                        │
│ list    List todo items in the list                                                               │
│ man     Show detailed help and context for settings, file format and heuristics                   │
│ undone  Mark one or more todo items as NOT done (undone)                                          │
╰───────────────────────────────────────────────────────────────────────────────────────────────────╯

 DrTodo can manage items in a global todo list (~/.drtodo/TODO.md) and in a local todo list
 (~/work/src/DrTodo/TODO.md).

 ```


# Settings

## Global Folder
- `~/.drtodo`                     global config folder
- `~/.drtodo/config.toml`         global config
- `~/.drtodo/config.USER.toml`    user specific config (in case this folder is shared)
- `~/.drtodo/TODO.md`             default location for todo list (configurable, and there could be more)
- `~/.drtodo/.git`                git repo for todo list (can be shared)

## Local Folder (under any git repo)
- `/somefolder/.git`              root folder for nearest .git repo (submodules NOT supported yet)
- `/somefolder/.drtodo.toml`      local config file for this git repo (safe to commit)
- `/somefolder/.drtodo.USER.toml` local config file for this git repo (safe to commit, ignored by other users)
- `/somefolder/TODO.md`           default location for todo list for this git repo (configurable)

## Environment variables

- `DRTODO_MDFILE`                default location for todo list
- `DRTODO_VERBOSE`               verbose output