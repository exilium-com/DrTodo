import re
from typing import Optional, Union


def parse_slice(s: str) -> slice:
    """
    parses a slice string like '1:3' and returns a tuple of (start, end) indexes.
    """
    split = s.split(':')
    if len(split) == 1:
        raise ValueError('slice must have at least one colon')
    return slice(*map(lambda x: int(x.strip()) if x.strip() else None, split))


# iterator to traverse tasks that match a spec, id, index or re match (or all)
def task_iterator(items: list, *,
                  spec: Optional[Union[int, str]] = None,
                  id: Optional[int] = None,
                  index: Optional[int] = None,
                  range: Optional[str] = None,
                  match: Optional[str] = None,
                  done: Optional[bool] = None,
                  omit_means_all: bool = False
):
    """
    iterates through all tasks that match the given criteria:
    - spec: a string that can be an index, an ID or a regular expression
    - id: a task ID (partial hexadecimal hash)
    - index: a task index
    - range: a range of task indexes (e.g. 1:3, can use negative indexes from end as well)
    - match: a regular expression to match against the task text
    - done: whether to match only done tasks or only tasks not done
    """
    if spec is not None:
        # heuristics:
        # if spec has a single : in it, assume it's a range
        # if spec is a small integer, assume it's a positive index
        # if spec is a a pure hex string assume it's an ID
        # otherwise assume it's a regular expression
        try:
            range = parse_slice(spec)
        except ValueError:
            try:
                index = int(spec)
                if index < 0 or index >= 1000:
                    raise ValueError
            except ValueError:
                if re.match(r'^[0-9a-f]+$', spec):
                    id = spec
                else:
                    match = spec

    if not omit_means_all and sum(spec is None, id is None, index is None, range is None, match is None, done is None) == 0:
        raise ValueError('no task selection criteria given')

    if isinstance(range, str):
        range = parse_slice(range)

    if isinstance(range, slice):
        import builtins
        range = builtins.range(*range.indices(len(items)))

    for item in items:
        if done is not None and item['checked'] != done:
            continue
        elif id is not None and not item['id'].startswith(id):
            continue
        elif index is not None and item['index'] != index:
            continue
        elif range is not None and item['index'] not in range:
            continue
        elif match is not None and not re.search(match, item['text']):
            continue
        yield item
