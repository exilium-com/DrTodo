# Settings

DrToDo allows plenty of configuration options that can be specialized by folder or per user.
There are many config files that can be used and are combined in specific ways detailed below.

> The default configuration is fine for most people, so you can just use skip this section, use `todo init` and start using DrToDo.

## TL;DR

Simplest case is `~/.drtodo/config.toml` which is the global config file created by `todo init`.
You can edit that file an example with defaults is provided [below](#sample-config-file).
TODO items are saved in `~/.drtodo/TODO.md` by default. You can change file names and locations,
where in the md file the TODO items go and the appearance of how TODO items are rendered.

## Config File Locations

There are two valid locations for config files, *global* and *local*. Global config files are located in
the `~/.drtodo` folder and local config files are located in the root of any git repo.

If you are under a git repo, and the root of the git repo has a DrToDo config file, it will run in *local* mode
(unless the `--global` option is provided). Otherwise it will run in *global* mode.

### Global Mode

In global mode, the global config file at `~/.drtodo/config.toml` is used. Every user starts in this mode.
There are *two* config files that are loaded in global mode, `~/.drtodo/config.toml` and `~/.drtodo/config.USER.toml`
(with `USER` replaced by the current user name). The `USER` config file is optional and is used to override the global
config values per user. This is useful if you want to share the global config file but have some user specific settings
(which you could also safely share as they wouldn't apply to anyone else).

The configuration is used to operate on the global todo file which by default is `~/.drtodo/TODO.md`, but can be overridden
in the config files with the `mdfile=SOMENAME.md` option.

### Local Mode

In local mode, the config file at the root of the current git repo is used. This file is named `.drtodo.toml` and again
there are two files that are loaded, `.drtodo.toml` and `.drtodo.USER.toml` (with `USER` replaced by the current user name).
These files can be safely committed to git and shared with other users. The `USER` config file is optional and is only loaded
for that user, so they can override the shared config file with their own settings.

> NOTE: whenever you run under a git repo that is configured for DrToDo, you will be in local mode by default.
> Use the `--global` option to change it.

### Example

Let's say you have this file structure:

```shell
~ (me)                      # home folder for user 'me'
├── .drtodo                 # global config folder
│   ├── config.toml         # [2] global config file
│   ├── TODO.md             # [2] global todo file
│   └── .git                # git repo for global todo file and config
└── work
    ├── someproject         # project under git
    │   ├── ...             # lots of files but no .drtodo files
    │   └── .git            # git repo for this project
    └── myproject           # project under git
        ├── .drtodo.toml    # [1] local config file for this project
        ├── .drtodo.me.toml # [1] personal config file for this project
        ├── BUGS.md         # [1] todo file configured in .drtodo.toml
        ├── ...             # lots of other files for myproject
        ├── somefolder      # some folder under myproject
        │   └── ...
        └── .git            # git repo for this project
```

```console
$ cd ~                          # home folder
$ todo list                     # run in global mode
~/.drtodo/TODO.md
  0: 662b404 [ ] feed the dog
$ cd work/myproject/somefolder  # folder under git
$ todo list                     # run in local mode
~/work/myproject/BUGS.md
  0: 7a787ec [ ] bug 1
  1: f237ece [ ] bug 2
$ todo --global list            # run in global mode
~/.drtodo/TODO.md
  0: 662b404 [ ] feed the dog
$ cd ~/work/someproject         # folder under git but not configured for DrToDo
$ todo list                     # run in global mode
~/.drtodo/TODO.md
  0: 662b404 [ ] feed the dog
```

Anywhere under `myproject` you can run `todo` and it will use the local config files and local
todo files tagged with `[1]` above. If you use the `--global` option, it will ignore the local
files (tagged with `[1]`) and use the global files (tagged with `[2]`). The same global files
will be used if you run anywhere else that is not under a git repo. Or if you run under a git
repo that is not configured for DrToDo (such as `someproject`).

# Config File Format

Config files are written in [TOML](http://toml.io/) format. TOML is a simple format that is easy to read and write.

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

# Reference

## Global Folder
- `~/.drtodo`                     global config folder
- `~/.drtodo/config.toml`         global config
- `~/.drtodo/config.USER.toml`    user specific config (in case this folder is shared)
- `~/.drtodo/TODO.md`             default location for todo list (configurable)
- `~/.drtodo/.git`                git repo for todo list (can be shared)

## Local Folder (under any git repo)
- `/somefolder/.git`              root folder for nearest .git repo (submodules NOT supported)
- `/somefolder/.drtodo.toml`      local config file for this git repo (safe to commit)
- `/somefolder/.drtodo.USER.toml` local config file for this git repo (safe to commit, ignored by other users)
- `/somefolder/TODO.md`           default location for todo list for this git repo (configurable)

## Environment variables

- `DRTODO_MDFILE`                default location for todo list
- `DRTODO_VERBOSE`               verbose output
- `DRTODO_IGNORE_CONFIG`         ignore all config files and use defaults
- `DRTODO_KEEP_BACKUPS`          number of old markdown file backups to keep

## Sample config file
```toml
{DEFAULT_CONFIG}
```
