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
            created_at=data['created_at']
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

@app.route('/')
def home():
    return render_template('index.html', posts=posts)

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
def create_post():
    # Get the post data from the request
    data = request.get_json()
    
    # Validate required fields
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'error': 'Title and content are required'}), 400
    
    # Create new blog post
    new_post = BlogPost(data['title'], data['content'])
    posts.append(new_post)
    
    # Save to JSON file
    save_posts(posts)
    
    # Return the created post
    return jsonify(new_post.to_dict()), 201

@app.route('/api/posts/<post_id>', methods=['PUT'])
def update_post(post_id):
    # Find the post with the given ID
    post = next((post for post in posts if post.id == post_id), None)
    if post is None:
        return jsonify({'error': 'Post not found'}), 404
    
    # Get the post data from the request
    data = request.get_json()
    
    # Validate required fields
    if not data or ('title' not in data and 'content' not in data):
        return jsonify({'error': 'Title or content is required'}), 400
    
    # Update the post
    if 'title' in data:
        post.title = data['title']
    if 'content' in data:
        post.content = data['content']
    
    # Save to JSON file
    save_posts(posts)
    
    # Return the updated post
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
    return redirect(url_for('home'))

# Frontend routes
@app.route('/posts/new', methods=['GET'])
def create_post_page():
    return render_template('create.html')

@app.route('/posts/create', methods=['POST'])
def create_post_submit():
    title = request.form.get('title')
    content = request.form.get('content')
    
    if not title or not content:
        return "Title and content are required!", 400
    
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            filename = f"{timestamp}-{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = f"uploads/{filename}"
    
    new_post = BlogPost(title, content, image_path=image_path)
    posts.append(new_post)
    save_posts(posts)
    
    return redirect(url_for('home'))

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
    
    title = request.form.get('title')
    content = request.form.get('content')
    
    if not title or not content:
        return "Title and content are required!", 400
    
    post.title = title
    post.content = content
    save_posts(posts)
    
    return redirect(url_for('home'))

if __name__ == '__main__':
    print("Starting Flask app on http://localhost:8000 ...")
    app.run(host='localhost', port=8000, debug=True)  # Try a different port
