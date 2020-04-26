"""
    History classes & helpers
    ~~~~~~~~~~~~~~~~~~~~~~
"""
import os
import json
import uuid

from datetime import datetime

import difflib


class HistoryManager(object):
    """A very simple history Manager, that saves it's data as json."""

    def __init__(self, path):
        self.file = os.path.join(path, 'history.json')

    def read(self):
        if not os.path.exists(self.file):
            return {}
        with open(self.file) as f:
            data = json.loads(f.read())
        return data

    def write(self, data):
        with open(self.file, 'w') as f:
            f.write(json.dumps(data, indent=2))

    def add_history(self, name, url, old_page, new_page):
        history = self.read()
        date = datetime.now().strftime('%#I:%M %p, %d %B %Y')
        old_page_data = HistoryDiffPage(old_page)
        new_page_data = HistoryDiffPage(new_page)
        new_history = {
            'id': str(uuid.uuid4()),
            'username': name,
            'date': date,
            'old_page': json.dumps(old_page_data.__dict__),
            'new_page': json.dumps(new_page_data.__dict__)
        }
        if url in history:
            history[url].append(new_history)
        else:
            history[url] = [new_history]
        self.write(history)

    def rename_page_history(self, url, newurl):
        history = self.read()
        history[newurl] = history.pop(url)
        self.write(history)

    def delete_history(self, url):
        history = self.read()
        if not history.pop(url, False):
            return False
        self.write(history)
        return True

    def get_history(self, url):
        history = self.read()
        page_history = history.get(url)
        if not page_history:
            return None
        return History(self, url, page_history)

    def get_history_diff(self, url, id):
        history = self.read()
        page_history = history.get(url)
        diff_to_return = []
        for hist in page_history:
            if hist['id'] == id:
                old_page = json.loads(hist['old_page'])
                new_page = json.loads(hist['new_page'])

                diff = difflib.ndiff(old_page['title'], new_page['title'])
                is_title_changed = False
                for l in diff:
                    if l.startswith('+ ') or l.startswith('- '):
                        is_title_changed = True
                        break
                diff_to_return.append(['Title', old_page['title'], new_page['title'], is_title_changed])

                diff = difflib.ndiff(old_page['body'], new_page['body'])
                is_body_changed = False
                for l in diff:
                    if l.startswith('+ ') or l.startswith('- '):
                        is_body_changed = True
                        break
                diff_to_return.append(['Body', old_page['body'], new_page['body'], is_body_changed])

                diff = difflib.ndiff(old_page['tags'], new_page['tags'])
                is_tags_changed = False
                for l in diff:
                    if l.startswith('+ ') or l.startswith('- '):
                        is_tags_changed = True
                        break
                diff_to_return.append(['Tags', old_page['tags'], new_page['tags'], is_tags_changed])

                break

        return diff_to_return


class History(object):
    def __init__(self, manager, url, data):
        self.manager = manager
        self.url = url
        self.data = data

    def get(self, option):
        return self.data.get(option)


class HistoryDiffPage(object):
    def __init__(self, data):
        self.title = data.title
        self.body = data.body
        self.tags = data.tags

    def get_title(self):
        return self.title

    def get_body(self):
        return self.body

    def get_tags(self):
        return self.tags
