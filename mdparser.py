
import mistune
from pathlib import Path
import re
from rich import print
from mistune.renderers.markdown import MarkdownRenderer


class TokenTraverser:

    def traverse_tokens(self, tokens, search_token_type, found_callback):
        for tok in tokens:
            if tok['type'] == search_token_type:
                found_callback(tok)
            if 'children' in tok:
                self.traverse_tokens(tok['children'], search_token_type, found_callback)
        return tokens


class TaskListTraverser(TokenTraverser):

    TASK_LIST_ITEM = re.compile(r'^(\[[ xX]\])\s+')

    @staticmethod
    def calc_git_hash(text):
        import hashlib
        return hashlib.sha1(text.encode('utf-8')).hexdigest()

    def find_task_lists(self, tokens) -> list:
        found_items = []

        def match_task_item(tok):
            if tok['type'] != 'list_item':
                return

            if 'task_list_item' in tok:
                # already processed in a previous traversal
                found_items.append(tok['task_list_item'])
                return

            children = tok['children']
            if children:
                text_list = []

                def append_text(t):
                    text_list.append(t['raw'])

                self.traverse_tokens(children, 'text', append_text)
                text = ''.join(text_list)
                m = TaskListTraverser.TASK_LIST_ITEM.match(text)
                if m:   # is it a task list item? if not, ignore it
                    mark = m.group(1)
                    item_text = text[m.end():].strip()
                    id = self.calc_git_hash(item_text)
                    task_list_item = {'checked': mark != '[ ]', 'text': item_text, 'id': id, 'index': len(found_items), 'token': tok}
                    tok['task_list_item'] = task_list_item
                    found_items.append(tok['task_list_item'])

        self.traverse_tokens(tokens, 'list_item', match_task_item)
        return found_items


def parse_todo_list(pathname: Path):
    markdownparser = mistune.create_markdown(renderer=MarkdownRenderer(), plugins=[])

    with open(pathname) as f:
        text = f.read()
        result, state = markdownparser.parse(text)
        # traverse the tokens
        items = TaskListTraverser().find_task_lists(state.tokens)

    return items
