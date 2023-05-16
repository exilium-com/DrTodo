import re

__all__ = ['task_lists', 'split_task_item']


TASK_LIST_ITEM = re.compile(r'^(\[[ xX]\])\s+')


def task_lists_hook(md, state):
    return _rewrite_all_list_items(state.tokens)


def task_lists(md):
    """A mistune plugin to support task lists. This will simply tag task list
    items with special attrs based on the parsed task list syntax. Spec defined by
    GitHub flavored Markdown and commonly used by many parsers:

    .. code-block:: text

        - [ ] unchecked task
        - [x] checked task

    :param md: Markdown instance
    """
    md.before_render_hooks.append(task_lists_hook)


def _rewrite_all_list_items(tokens):
    for tok in tokens:
        if tok['type'] == 'list_item':
            _rewrite_list_item(tok)
        if 'children' in tok:
            _rewrite_all_list_items(tok['children'])
    return tokens


def raise_no_match():
    raise ValueError


def split_task_item(rawtext: str) -> (bool, str):
    m = TASK_LIST_ITEM.match(rawtext) or raise_no_match()
    mark = m.group(1)
    return mark != '[ ]', rawtext[m.end():]


def _rewrite_list_item(tok):
    children = tok['children']
    if children:
        first_child = children[0]
        rawtext = first_child.get('text', '')
        try:
            checked, text = split_task_item(rawtext)
            tok['attrs'] = {'checked': checked, 'task_text': text}
        except ValueError:
            pass
