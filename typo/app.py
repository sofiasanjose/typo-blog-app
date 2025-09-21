from flask import Flask, jsonify, request
from datetime import datetime
import json
import os

app = Flask(__name__)

# File path for JSON storage
POSTS_FILE = os.path.join(os.path.dirname(__file__), 'posts.json')

# Data model for a blog post
class BlogPost:
    def __init__(self, title, content, id=None, created_at=None):
        self.id = id if id else str(datetime.now().timestamp())
        self.title = title
        self.content = content
        self.created_at = created_at if created_at else datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at
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
    return "<h1>Hello, Typo Blog!</h1>"

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
def delete_post(post_id):
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

if __name__ == '__main__':
    print("Starting Flask app on http://localhost:8000 ...")
    app.run(host='localhost', port=8000, debug=True)  # Try a different port
