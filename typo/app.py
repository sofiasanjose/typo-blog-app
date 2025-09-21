from flask import Flask, jsonify, request, render_template, redirect, url_for, send_from_directory
from datetime import datetime
from werkzeug.utils import secure_filename
import json
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static/uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# File path for JSON storage
POSTS_FILE = os.path.join(os.path.dirname(__file__), 'posts.json')

# Data model for a blog post
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class BlogCustomization:
    def __init__(self):
        self.header_image = None
        self.bg_style = 'gradient1'
    
    def to_dict(self):
        return {
            'header_image': self.header_image,
            'bg_style': self.bg_style
        }
    
    @classmethod
    def from_dict(cls, data):
        customization = cls()
        customization.header_image = data.get('header_image')
        customization.bg_style = data.get('bg_style', 'gradient1')
        return customization

class BlogPost:
    def __init__(self, title, content, id=None, created_at=None, image_path=None):
        self.id = id if id else str(datetime.now().timestamp())
        self.title = title
        self.content = content
        self.created_at = created_at if created_at else datetime.now().isoformat()
        self.image_path = image_path

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at,
            'image_path': self.image_path
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            title=data['title'],
            content=data['content'],
            id=data['id'],
            created_at=data['created_at'],
            image_path=data.get('image_path')
        )

# JSON file operations
def load_posts():
    if not os.path.exists(POSTS_FILE):
        return []
    try:
        with open(POSTS_FILE, 'r') as f:
            data = json.load(f)
            return [BlogPost.from_dict(post) for post in data]
    except json.JSONDecodeError:
        return []

def save_posts(posts):
    with open(POSTS_FILE, 'w') as f:
        json.dump([post.to_dict() for post in posts], f, indent=2)

# Initialize posts from file
posts = load_posts()

CUSTOMIZATION_FILE = os.path.join(os.path.dirname(__file__), 'customization.json')

def load_customization():
    if os.path.exists(CUSTOMIZATION_FILE):
        try:
            with open(CUSTOMIZATION_FILE, 'r') as f:
                return BlogCustomization.from_dict(json.load(f))
        except json.JSONDecodeError:
            return BlogCustomization()
    return BlogCustomization()

def save_customization(customization):
    with open(CUSTOMIZATION_FILE, 'w') as f:
        json.dump(customization.to_dict(), f, indent=2)

customization = load_customization()

@app.route('/')
def home():
    return render_template('landing.html')

@app.route('/feed')
def feed():
    return render_template('index.html', posts=posts, customization=customization)

@app.route('/customize', methods=['GET'])
def customize():
    return render_template('customize.html', customization=customization)

@app.route('/customize', methods=['POST'])
def save_customization_route():
    if 'header_image' in request.files:
        file = request.files['header_image']
        if file and file.filename:  # Check if a file was actually selected
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                filename = f"header-{timestamp}-{filename}"
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # Remove old header image if it exists
                if customization.header_image:
                    old_path = os.path.join(app.static_folder, customization.header_image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                customization.header_image = f"uploads/{filename}"
    
    bg_style = request.form.get('bg_style')
    if bg_style:
        customization.bg_style = bg_style
    
    save_customization(customization)
    return redirect(url_for('customize'))

@app.route('/api/posts', methods=['GET'])
def get_posts():
    # Return all posts
    return jsonify([post.to_dict() for post in posts])

@app.route('/api/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    # Find the post with the given ID
    post = next((post for post in posts if post.id == post_id), None)
    if post is None:
        return jsonify({'error': 'Post not found'}), 404
    return jsonify(post.to_dict())

@app.route('/api/posts', methods=['POST'])
def create_post_api():
    # Get the post data from the request
    data = request.get_json()
    
    # Validate required fields
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'error': 'Title and content are required'}), 400
    
    # Create new blog post
    new_post = BlogPost(title=data['title'], content=data['content'])
    posts.append(new_post)
    save_posts(posts)
    return jsonify(new_post.to_dict()), 201

@app.route('/api/posts/<post_id>', methods=['PUT'])
def update_post(post_id):
    # Get the post data from the request
    data = request.get_json()
    
    # Find the post with the given ID
    post = next((post for post in posts if post.id == post_id), None)
    if post is None:
        return jsonify({'error': 'Post not found'}), 404
    
    # Update post data
    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    
    # Save changes
    save_posts(posts)
    return jsonify(post.to_dict())

@app.route('/api/posts/<post_id>', methods=['DELETE'])
def delete_post_api(post_id):
    # Find the post with the given ID
    post = next((post for post in posts if post.id == post_id), None)
    if post is None:
        return jsonify({'error': 'Post not found'}), 404
    
    # Remove the post from the list
    posts.remove(post)
    
    # Save to JSON file
    save_posts(posts)
    
    # Return success message
    return jsonify({'message': 'Post deleted successfully'}), 200

@app.route('/posts/<post_id>/delete', methods=['POST'])
def delete_post(post_id):
    # Find the post with the given ID
    post = next((post for post in posts if post.id == post_id), None)
    if post is None:
        return "Post not found!", 404
    
    # Remove the post from the list
    posts.remove(post)
    
    # Save to JSON file
    save_posts(posts)
    
    # Redirect back to home page
    return redirect(url_for('feed'))

# Frontend routes
@app.route('/posts/new', methods=['GET'])
def create_post_page():
    return render_template('create.html')

@app.route('/posts/create', methods=['POST'])
def create_post():
    title = request.form.get('title')
    content = request.form.get('content')
    image = None
    
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            filename = f"{timestamp}-{filename}"
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image = f"uploads/{filename}"
    
    new_post = BlogPost(title=title, content=content, image_path=image)
    posts.insert(0, new_post)  # Add new posts at the beginning
    save_posts(posts)
    return redirect(url_for('feed'))

@app.route('/posts/<post_id>/edit', methods=['GET'])
def edit_post_page(post_id):
    post = next((post for post in posts if post.id == post_id), None)
    if post is None:
        return "Post not found!", 404
    return render_template('edit.html', post=post)

@app.route('/posts/<post_id>/update', methods=['POST'])
def update_post_submit(post_id):
    post = next((post for post in posts if post.id == post_id), None)
    if post is None:
        return "Post not found!", 404
    
    post.title = request.form.get('title', post.title)
    post.content = request.form.get('content', post.content)
    
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            if allowed_file(file.filename):
                # Remove old image if it exists
                if post.image_path:
                    old_path = os.path.join(app.static_folder, post.image_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                filename = f"{timestamp}-{filename}"
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                post.image_path = f"uploads/{filename}"
    
    save_posts(posts)
    return redirect(url_for('feed'))

if __name__ == '__main__':
    print("Starting Flask app on http://localhost:8000 ...")
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True, port=8000)
