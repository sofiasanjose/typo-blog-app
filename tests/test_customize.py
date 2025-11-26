from typo import app as typo_app
import io


def test_customize_save_and_cleanup(tmp_path, monkeypatch):
    tmp_custom = tmp_path / 'custom.json'
    monkeypatch.setattr(typo_app, 'CUSTOMIZATION_FILE', str(tmp_custom))
    uploads = tmp_path / 'uploads'
    uploads.mkdir()
    monkeypatch.setitem(typo_app.app.config, 'UPLOAD_FOLDER', str(uploads))
    # reset customization
    monkeypatch.setattr(typo_app, 'customization', typo_app.BlogCustomization(), raising=False)

    client = typo_app.app.test_client()

    data = {
        'bg_style': 'gradient3',
        'header_image': (io.BytesIO(b'header'), 'header.png')
    }

    resp = client.post('/customize', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert resp.status_code in (200, 302)

    # load customization file
    assert tmp_custom.exists()
    with open(tmp_custom, 'r') as f:
        import json
        d = json.load(f)
    assert d.get('bg_style') == 'gradient3'
