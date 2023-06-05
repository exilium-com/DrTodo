# Markdown Files

By default, {appname} will look for any lists formatted as GitHub-style task lists in
any Markdown files it reads.

For example a file containing this:
```markdown
This is my cool project readme file.

## TODO
- [x] write a readme
- [ ] make it useful

## Bugs assigned to me
- [ ] bug 1
- [ ] bug 2
```

Will produce the following output:
```console
$ todo list
~/work/src/DrTodo/TODO.md
  0: 56a01da 🔘 write a readme
  1: 5869ea7 ⚫ make it useful
  2: 7a787ec ⚫ bug 1
  3: f237ece ⚫ bug 2
```

All items will be logically combined into a single list and listed together.

> In the future, it will be possible to specify which section in a Markdown file to use as a list,
> and then all other lists will be ignored.

> Also, we will have options to add to the bottom or to the top (meaning right before or right after the
> last task list item).
