import json
import os
import importlib

import pytest


def test_save_and_load_posts(tmp_path, monkeypatch):
    app = importlib.import_module('typo.app')
    tmp_file = tmp_path / 'posts.json'
    # point POSTS_FILE to temp file
    monkeypatch.setattr(app, 'POSTS_FILE', str(tmp_file))

    # start with empty
    posts = []
    from typo.app import BlogPost
    p = BlogPost(title='T', content='C')
    posts.append(p)
    app.save_posts(posts)
    loaded = app.load_posts()
    assert len(loaded) == 1
    assert loaded[0].title == 'T'
