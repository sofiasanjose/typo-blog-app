import io
from typo import app as typo_app


def test_file_upload_and_post_create(tmp_path, monkeypatch):
    # Setup temp env
    tmp_posts = tmp_path / 'posts.json'
    monkeypatch.setattr(typo_app, 'POSTS_FILE', str(tmp_posts))
    uploads = tmp_path / 'uploads'
    uploads.mkdir()
    monkeypatch.setitem(typo_app.app.config, 'UPLOAD_FOLDER', str(uploads))
    monkeypatch.setattr(typo_app, 'posts', [], raising=False)

    client = typo_app.app.test_client()

    data = {
        'title': 'UploadTest',
        'content': 'Has image',
        'image': (io.BytesIO(b'fake-image-bytes'), 'test.jpg')
    }

    resp = client.post('/posts/create', data=data, content_type='multipart/form-data', follow_redirects=True)
    # after redirect, should load feed page
    assert resp.status_code in (200, 302)

    # Check that file was saved
    saved_files = list(uploads.iterdir())
    assert any(f.name.endswith('.jpg') for f in saved_files)
