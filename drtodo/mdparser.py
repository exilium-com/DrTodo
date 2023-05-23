
import mistune
from pathlib import Path
from mistune.renderers.markdown import MarkdownRenderer
from .mistuneplugin import task_lists


class TokenTraverser:

    def traverse_tokens(self, tokens, search_token_type, found_callback):
        for tok in tokens:
            if tok['type'] == search_token_type:
                found_callback(tok, tokens)
            if 'children' in tok:
                self.traverse_tokens(tok['children'], search_token_type, found_callback)
        return tokens


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

    def find_task_lists(self, tokens) -> list:
        found_items = []

        def match_task_item(tok, parent_tokens):
            if tok['type'] != 'list_item':
                return
            if 'attrs' not in tok or 'checked' not in tok['attrs']:
                # not a task recognized by the mistune plugin
                return

            if 'task_item' in tok:
                # already processed in a previous traversal
                found_items.append(tok['task_item'])
                return

            children = tok['children']
            if children:
                task_item = self.create_item(tok['attrs']['task_text'],
                                             index=len(found_items),
                                             checked=tok['attrs']['checked'],
                                             token=tok)
                task_item['parent'] = parent_tokens
                found_items.append(tok['task_item'])

        self.traverse_tokens(tokens, 'list_item', match_task_item)
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
