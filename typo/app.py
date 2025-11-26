"""
Typo Blog Application

A minimalist blog application built with Flask that provides CRUD functionality
for blog posts with image upload support and customizable themes.

Features:
- Create, read, update, delete blog posts
- Image upload and management
- JSON-based data persistence
- Blog customization (header images, background styles)
- Clean, responsive web interface

Author: Sofia Claudia San Jose Bonoan
Date: October 2025
"""

from flask import Flask, jsonify, request, render_template, redirect, url_for, g
from datetime import datetime
from werkzeug.utils import secure_filename
import json
import os
import time

# Prometheus client for metrics
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Flask application configuration
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static/uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size limit

# Security: Define allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# File paths for JSON data storage
POSTS_FILE = os.path.join(os.path.dirname(__file__), 'posts.json')

# Application start time for health reporting
APP_START_TIME = time.time()

# Prometheus metrics
REQUEST_COUNT = Counter('typo_request_count', 'Total Request Count', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('typo_request_latency_seconds', 'Request latency', ['endpoint'])
ERROR_COUNT = Counter('typo_error_count', 'Total error count', ['endpoint'])

# Data model for a blog post
def allowed_file(filename):
    """
    Check if uploaded file has an allowed extension.
    
    Args:
        filename (str): Name of the uploaded file
        
    Returns:
        bool: True if file extension is allowed, False otherwise
    """
    # Check if filename has extension and if it's in allowed list
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class BlogCustomization:
    """
    Model class for blog customization settings.
    Handles header image and background style preferences.
    """
    def __init__(self):
        """Initialize with default customization settings."""
        self.header_image = None  # Path to header image file
        self.bg_style = 'gradient1'  # Default background style
    
    def to_dict(self):
        """
        Convert customization object to dictionary for JSON serialization.
        
        Returns:
            dict: Dictionary representation of customization settings
        """
        return {
            'header_image': self.header_image,
            'bg_style': self.bg_style
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Create BlogCustomization object from dictionary data.
        
        Args:
            data (dict): Dictionary containing customization data
            
        Returns:
            BlogCustomization: New customization object with loaded data
        """
        customization = cls()
        customization.header_image = data.get('header_image')
        # Use default gradient1 if bg_style not specified
        customization.bg_style = data.get('bg_style', 'gradient1')
        return customization

class BlogPost:
    """
    Model class representing a blog post with title, content, and optional image.
    Handles automatic ID generation and timestamp creation.
    """
    def __init__(self, title, content, id=None, created_at=None, image_path=None):
        """
        Initialize a new blog post.
        
        Args:
            title (str): Post title
            content (str): Post content/body
            id (str, optional): Unique post ID, auto-generated if not provided
            created_at (str, optional): ISO timestamp, auto-generated if not provided
            image_path (str, optional): Relative path to post image
        """
        # Generate unique ID using timestamp if not provided
        self.id = id if id else str(datetime.now().timestamp())
        self.title = title
        self.content = content
        # Generate ISO format timestamp if not provided
        self.created_at = created_at if created_at else datetime.now().isoformat()
        self.image_path = image_path

    def to_dict(self):
        """
        Convert blog post object to dictionary for JSON serialization.
        
        Returns:
            dict: Dictionary representation of the blog post
        """
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at,
            'image_path': self.image_path
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create BlogPost object from dictionary data loaded from JSON.
        
        Args:
            data (dict): Dictionary containing post data
            
        Returns:
            BlogPost: New blog post object with loaded data
        """
        return cls(
            title=data['title'],
            content=data['content'],
            id=data.get('id'),  # Use .get() for optional fields
            created_at=data.get('created_at'),
            image_path=data.get('image_path')
        )

# JSON file operations
def load_posts():
    """
    Load blog posts from JSON file and convert to BlogPost objects.
    
    Returns:
        list: List of BlogPost objects, empty list if file doesn't exist or is corrupted
    """
    # Check if posts file exists, return empty list if not
    if not os.path.exists(POSTS_FILE):
        return []
    
    try:
        # Open and parse JSON file
        with open(POSTS_FILE, 'r') as f:
            data = json.load(f)
            # Convert each dictionary to BlogPost object using class method
            return [BlogPost.from_dict(post) for post in data]
    except json.JSONDecodeError:
        # Return empty list if JSON is corrupted or invalid
        return []

def save_posts(posts):
    """
    Save list of BlogPost objects to JSON file.
    
    Args:
        posts (list): List of BlogPost objects to save
    """
    # Convert BlogPost objects to dictionaries and save to file with formatting
    with open(POSTS_FILE, 'w') as f:
        json.dump([post.to_dict() for post in posts], f, indent=2)

# Initialize blog posts by loading from JSON file at startup
posts = load_posts()

# File path for customization settings storage
CUSTOMIZATION_FILE = os.path.join(os.path.dirname(__file__), 'customization.json')

def load_customization():
    """
    Load blog customization settings from JSON file.
    
    Returns:
        BlogCustomization: Customization object with settings, or default if file missing/corrupted
    """
    # Check if customization file exists
    if os.path.exists(CUSTOMIZATION_FILE):
        try:
            # Load and parse customization data from JSON
            with open(CUSTOMIZATION_FILE, 'r') as f:
                return BlogCustomization.from_dict(json.load(f))
        except json.JSONDecodeError:
            # Return default customization if JSON is corrupted
            return BlogCustomization()
    # Return default customization if file doesn't exist
    return BlogCustomization()

def save_customization(customization):
    """
    Save blog customization settings to JSON file.
    
    Args:
        customization (BlogCustomization): Customization object to save
    """
    # Convert to dictionary and save with pretty formatting
    with open(CUSTOMIZATION_FILE, 'w') as f:
        json.dump(customization.to_dict(), f, indent=2)

# Initialize blog customization by loading from JSON file at startup
customization = load_customization()

@app.route('/')
def home():
    return render_template('landing.html')


@app.before_request
def start_timer():
    # start request timer for metrics
    g._start_time = time.time()


@app.after_request
def record_metrics(response):
    try:
        latency = time.time() - getattr(g, '_start_time', time.time())
        endpoint = request.path
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
        REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, http_status=response.status_code).inc()
    except Exception:
        # don't let metrics break responses
        pass
    return response


@app.errorhandler(Exception)
def handle_exception(e):
    # increment error metric and return generic error response
    try:
        ERROR_COUNT.labels(endpoint=request.path).inc()
    except Exception:
        pass
    return jsonify({'error': 'Internal server error'}), 500


@app.route('/health', methods=['GET'])
def health():
    uptime = time.time() - APP_START_TIME
    return jsonify({'status': 'ok', 'uptime_seconds': int(uptime)})


@app.route('/metrics')
def metrics():
    # Expose Prometheus metrics
    resp = generate_latest()
    return (resp, 200, {'Content-Type': CONTENT_TYPE_LATEST})

@app.route('/feed')
def feed():
    return render_template('index.html', posts=posts, customization=customization)

@app.route('/customize', methods=['GET'])
def customize():
    return render_template('customize.html', customization=customization)

@app.route('/customize', methods=['POST'])
def save_customization_route():
    """
    Handle POST request to save blog customization settings.
    Processes header image upload and background style selection.
    """
    # Process header image upload if provided
    if 'header_image' in request.files:
        file = request.files['header_image']
        # Check if a file was actually selected (not empty)
        if file and file.filename:
            # Validate file type against allowed extensions
            if allowed_file(file.filename):
                # Secure the filename to prevent directory traversal attacks
                filename = secure_filename(file.filename)
                # Add timestamp to prevent filename conflicts
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                filename = f"header-{timestamp}-{filename}"
                
                # Ensure upload directory exists
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                
                # Save the uploaded file
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                # Clean up: remove old header image if it exists
                if customization.header_image:
                    old_path = os.path.join(app.static_folder, customization.header_image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                # Update customization with new image path
                customization.header_image = f"uploads/{filename}"
    
    # Process background style selection
    bg_style = request.form.get('bg_style')
    if bg_style:
        customization.bg_style = bg_style
    
    # Persist changes to file
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
    """
    Handle POST request to create a new blog post.
    Processes form data including optional image upload.
    """
    # Extract form data
    title = request.form.get('title')
    content = request.form.get('content')
    image = None
    
    # Process optional image upload
    if 'image' in request.files:
        file = request.files['image']
        # Validate file exists and is allowed type
        if file and allowed_file(file.filename):
            # Secure filename and add timestamp to prevent conflicts
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            filename = f"{timestamp}-{filename}"
            
            # Ensure upload directory exists
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            
            # Save file and store relative path
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image = f"uploads/{filename}"
    
    # Create new blog post object
    new_post = BlogPost(title=title, content=content, image_path=image)
    # Insert at beginning to show newest posts first
    posts.insert(0, new_post)
    # Persist changes to JSON file
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
    """
    Handle POST request to update an existing blog post.
    Updates title, content, and optionally replaces image.
    
    Args:
        post_id (str): Unique identifier of the post to update
    """
    # Find the post by ID using generator expression
    post = next((post for post in posts if post.id == post_id), None)
    if post is None:
        return "Post not found!", 404
    
    # Update post fields with form data, keeping existing values as fallback
    post.title = request.form.get('title', post.title)
    post.content = request.form.get('content', post.content)
    
    # Process optional image update
    if 'image' in request.files:
        file = request.files['image']
        # Check if new image file was provided
        if file and file.filename:
            if allowed_file(file.filename):
                # Clean up: remove old image file to save disk space
                if post.image_path:
                    old_path = os.path.join(app.static_folder, post.image_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                # Process new image file with secure naming
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
                filename = f"{timestamp}-{filename}"
                
                # Ensure upload directory exists
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                
                # Save new image and update post reference
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                post.image_path = f"uploads/{filename}"
    
    # Persist all changes to JSON file
    save_posts(posts)
    return redirect(url_for('feed'))

if __name__ == '__main__':
    """
    Main execution block - runs when script is executed directly.
    Sets up upload directory and starts Flask development server.
    """
    print("Starting Flask app on http://localhost:8000 ...")
    
    # Ensure upload directory exists before starting server
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Start Flask development server with debug mode enabled
    app.run(debug=True, port=8000)
