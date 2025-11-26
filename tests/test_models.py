import pytest
from typo.app import BlogPost, BlogCustomization


def test_blogpost_to_from_dict():
    post = BlogPost(title='Hi', content='Content', image_path='uploads/img.jpg')
    d = post.to_dict()
    new = BlogPost.from_dict(d)
    assert new.title == 'Hi'
    assert new.content == 'Content'
    assert new.image_path == 'uploads/img.jpg'


def test_customization_to_from_dict():
    c = BlogCustomization()
    c.header_image = 'uploads/header.png'
    c.bg_style = 'gradient2'
    d = c.to_dict()
    nc = BlogCustomization.from_dict(d)
    assert nc.header_image == 'uploads/header.png'
    assert nc.bg_style == 'gradient2'
