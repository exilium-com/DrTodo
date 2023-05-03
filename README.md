This is a sample list of TODOs locally tracked in this git repo.

To Do:
- [x] @WarpedPixel this is ~~to be~~ done
- [ ] to do by 2/3/23 #32


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