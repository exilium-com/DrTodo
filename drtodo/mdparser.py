import mistune
from pathlib import Path
from mistune.renderers.markdown import MarkdownRenderer
from .mistuneplugin import task_lists
from typing import Callable

from .settings import settings

class TokenTraverser:

    @staticmethod
    def tokens_by_type(tokens, search_token_type):
        """
        iterator that returns all tokens of type search_token_type.
        Ex: list(find_tokens(tokens, 'list_item')))
        """
        for tok in tokens:
            if tok['type'] == search_token_type:
                yield tok
            if 'children' in tok:
                yield from TokenTraverser.find_tokens(tok['children'], search_token_type)

    @staticmethod
    def traverse_tokens(tokens, callback: Callable[[], bool]):
        """
        traverse tokens calling the callback for each token. Return True to continue traversal or False to stop.
        """
        for tok in tokens:
            if not callback(tok, tokens):
                return
            if 'children' in tok:
                TokenTraverser.traverse_tokens(tok['children'], callback)


class TaskListTraverser(TokenTraverser):

    @staticmethod
    def calc_git_hash(text):
        import hashlib
        return hashlib.sha1(text.encode('utf-8')).hexdigest()

    @staticmethod
    def create_item(text, *, index: int, checked: bool = False, token: dict = None) -> dict:
        """
        creates a dict to represent a task list item from text and an index.
        If token is given, it is used, otherwise a new one is created.
        """
        id = TaskListTraverser.calc_git_hash(text.strip())  # always ignore leading and trailing whitespace for hash
        token = token or TaskListTraverser.create_item_token(checked, text)
        item = {'checked': checked, 'text': text, 'id': id, 'index': index, 'token': token}
        token['task_item'] = item
        return item

    @staticmethod
    def create_item_token(checked: bool, text: str) -> dict:
        return {
            'type': 'list_item',
            'children': [{'type': 'block_text', 'children': [{'type': 'text', 'raw': text}]}],
            'attrs': {'checked': checked, 'task_text': text}
        }

    @staticmethod
    def capture_all_text(tok: dict) -> str:
        if 'children' in tok:
            return ''.join([t['raw'] for t in TokenTraverser.tokens_by_type(tok['children'], 'text') if t['raw']])
        elif 'raw' in tok:
            return tok['raw']
        else:
            return ''

    def find_task_lists(self, tokens: list[dict]) -> list:
        found_items = []

        if settings.section:
            # we will only look for tasks in the section with the given name and optional level
            # parse the section name and level e.g. "## section name", "section name", etc.
            s = settings.section.lstrip('#')
            selected_section = { 'level': len(settings.section) - len(s),
                                 'name': s.strip().casefold(),
                                 'current': False }
        else:
            selected_section = { 'level': None, 'name': None, 'current': True }

        def match_task_item(tok, parent_tokens) -> bool:
            if tok['type'] == 'heading':
                if selected_section['name']:
                    if (not selected_section['level'] or tok['attrs']['level'] == selected_section['level']) and \
                        selected_section['name'] == self.capture_all_text(tok).strip().casefold():
                        selected_section['current'] = True
                    else:
                        selected_section['current'] = False
            if not selected_section['current']:
                return True
            if tok['type'] != 'list_item':
                return True
            if 'attrs' not in tok or 'checked' not in tok['attrs']:
                # not a task recognized by the mistune plugin
                return True

            if 'task_item' in tok:
                # already processed in a previous traversal
                found_items.append(tok['task_item'])
                return True

            children = tok['children']
            if children:
                task_item = self.create_item(tok['attrs']['task_text'],
                                             index=len(found_items),
                                             checked=tok['attrs']['checked'],
                                             token=tok)
                task_item['parent'] = parent_tokens
                found_items.append(tok['task_item'])

            return True

        self.traverse_tokens(tokens, match_task_item)
        return found_items


class TodoListParser:

    def __init__(self):
        self.markdownparser = mistune.create_markdown(renderer=MarkdownRenderer(), plugins=[task_lists])
        self.items = []
        self.state = None

    def parse(self, pathname: Path) -> list:
        with open(pathname) as f:
            text = f.read()
            result, state = self.markdownparser.parse(text)
            # traverse the tokens
            self.items = TaskListTraverser().find_task_lists(state.tokens)
            self.state = state
        return self.items

    def add_item_after(self, *, add: dict, after: dict):
        """Add a new item 'add' to the items and state after the given item 'after'"""
        # first find the index of the 'after' token in the parent list. if it fails we don't mess with the state
        relative_index = after['parent'].index(after['token']) + 1

        self.items.insert(after['index'] + 1, add)
        # reindex all the items now
        for i, item in enumerate(self.items):
            item['index'] = i
        # add the token to the state, by adding to the parent token (which is a list) after the 'after' token
        after['parent'].insert(relative_index, add['token'])
        # done
        # from rich import print
        # print(after['parent'])

    def _update_md_from_items(self):
        """Update the markdown text from the updated state in the items. Must be called before write()"""
        for item in self.items:
            token = item['token']
            token['attrs']['checked'] = item['checked']
            text_part = item['text'][:-1] if item['text'].endswith('\n') else item['text']   # trim just \n
            rawtext = f"[{'x' if item['checked'] else ' '}] {text_part}"
            assert token['children'][0]['type'] == 'block_text'
            # overwrite the children as a simple text token
            token['children'][0]['children'] = [{'type': 'text', 'raw': rawtext}]

    def write(self, pathname: Path):
        self._update_md_from_items()
        mdtext = self.markdownparser.render_state(self.state)
        with open(pathname, 'w') as f:
            f.write(mdtext)
