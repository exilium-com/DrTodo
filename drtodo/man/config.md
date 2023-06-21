# Settings

DrTodo allows plenty of configuration options that can be specialized by folder or per user.
There are many config files that can be used and are combined in specific ways detailed below.
Simplest case is `~/.drtodo/config.toml` which is the global config file.

## All Options

The primary options are below with their default values. You can override any of these in a toml config file.

```toml
    mdfile = 'TODO.md'      # default markdown file to use
    verbose = false         # verbose output
    keep_backups = 3        # number of old md file backups to keep
    hide_hash = false       # don't show hash (use index or RE instead)
```


### Style

Style can be either configured at a high level by name or configured in detailed individual settings.
High level configuration is easy, just set the `style` option as follows:

```toml
style = 'round'
```

Valid options for style are:

- 'round': 🔘/⚫
- 'ascii': [x]/[ ]
- 'bright': ✅/❌
- 'check': ✓/✗
- 'boxed': ☑/☐
- 'dark': ✅/🔳
- 'light': ✅/🔲

#### Detailed Style Configuration

If you want to configure the style in more detail, you can do so with any of these options:

```toml
[style]
checked = '🔘'              # emoji or symbols used for done items
unchecked = '⚫'            # emoji or symbols used for undone items
strike_done = False         # strike through done items
dim_done = False            # dim done items
index = 'bright_black'      # color of index
hash = 'italic dim yellow'  # color of hash
text = 'white'              # color of TODO text
header = 'bold cyan'        # color of header
warning = 'bold yellow'     # color of warnings
error = 'red'               # color of errors
```

All the colors above use the rich style and color names.
See [rich docs](https://rich.readthedocs.io/en/latest/style.html#style) for more info.

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
- `DRTODO_IGNORE_CONFIG`         ignore all config files and use defaults
- `DRTODO_KEEP_BACKUPS`          number of old markdown file backups to keep

## Sample config file (TOML)
```toml
{DEFAULT_CONFIG}
```
