import io
import json
import tempfile
from typo import app as typo_app


def setup_temp_env(tmp_path, monkeypatch):
    # Redirect POSTS_FILE and uploads to temp paths and clear in-memory posts
    tmp_posts = tmp_path / 'posts.json'
    monkeypatch.setattr(typo_app, 'POSTS_FILE', str(tmp_posts))
    uploads = tmp_path / 'uploads'
    uploads.mkdir()
    monkeypatch.setitem(typo_app.app.config, 'UPLOAD_FOLDER', str(uploads))
    # reset in-memory posts
    monkeypatch.setattr(typo_app, 'posts', [], raising=False)
    return tmp_posts, uploads


def test_api_crud(tmp_path, monkeypatch):
    tmp_posts, uploads = setup_temp_env(tmp_path, monkeypatch)
    client = typo_app.app.test_client()

    # Create post
    resp = client.post('/api/posts', json={'title': 'T1', 'content': 'C1'})
    assert resp.status_code == 201
    data = resp.get_json()
    post_id = data['id']
    assert data['title'] == 'T1'

    # Get all posts
    resp = client.get('/api/posts')
    assert resp.status_code == 200
    all_posts = resp.get_json()
    assert isinstance(all_posts, list) and len(all_posts) == 1

    # Get single post
    resp = client.get(f'/api/posts/{post_id}')
    assert resp.status_code == 200
    single = resp.get_json()
    assert single['title'] == 'T1'

    # Update post
    resp = client.put(f'/api/posts/{post_id}', json={'title': 'T1-upd'})
    assert resp.status_code == 200
    updated = resp.get_json()
    assert updated['title'] == 'T1-upd'

    # Delete post
    resp = client.delete(f'/api/posts/{post_id}')
    assert resp.status_code == 200
    # Ensure gone
    resp = client.get(f'/api/posts/{post_id}')
    assert resp.status_code == 404
