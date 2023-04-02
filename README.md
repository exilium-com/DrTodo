This is a sample list of TODOs locally tracked in this git repo.

To Do:
- [x] @WarpedPixel this is ~~to be~~ done
- [ ] to do by 2/3/23 #32


# Command line options

```console
$ todo --help

 Usage: python -m todo [OPTIONS] COMMAND [ARGS]...

 DrTodo, MD: a straightforward todo list manager for markdown files in git
 repos.

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --install-completion        [bash|zsh|fish|powershe  Install completion for  │
│                             ll|pwsh]                 the specified shell.    │
│                                                      [default: None]         │
│ --show-completion           [bash|zsh|fish|powershe  Show completion for the │
│                             ll|pwsh]                 specified shell, to     │
│                                                      copy it or customize    │
│                                                      the installation.       │
│                                                      [default: None]         │
│ --help                                               Show this message and   │
│                                                      exit.                   │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Global Options ─────────────────────────────────────────────────────────────╮
│ --settings  -s      PATH  Settings file to use                               │
│                           [default: /Users/bcs/.drtodo]                      │
│ --verbose   -v            Verbose output                                     │
│ --version   -V            Show version and exit                              │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ File Selection Options ─────────────────────────────────────────────────────╮
│ --mdfile        PATH  Markdown file to use for todo list                     │
│                       [default: TODO.md]                                     │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ add    Add a new todo item to the list                                       │
│ debug  List configuration, settings, version and other debug info.           │
│ done   Mark one or more todo items as done                                   │
│ init   Initialize DrTodo folder and files                                    │
│ list   List todo items in the list                                           │
│ man    Show detailed help and context for settings, file format and          │
│        heuristics                                                            │
╰──────────────────────────────────────────────────────────────────────────────╯

 DrTodo can manage items in a global todo list (~/.drtodo/TODO.md) and in a
 local todo list (~/work/src/DrTodo/TODO.md).

```
