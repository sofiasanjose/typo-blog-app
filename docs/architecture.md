# Project Architecture

## System Overview

```
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|  Web Interface   | --> |  Flask Backend   | --> |  JSON Storage   |
|  (HTML/CSS)      |     |  (app.py)       |     |  (posts.json)   |
|                  |     |                  |     |                  |
+------------------+     +------------------+     +------------------+
                               |
                               v
                        +------------------+
                        |                  |
                        |  Static Files    |
                        |  (images/css)    |
                        |                  |
                        +------------------+

```

## Component Description

### 1. Web Interface
- HTML templates for user interaction
- CSS for styling and layout
- Located in `/templates` and `/static/css`

### 2. Flask Backend (app.py)
- Main application logic
- Handles HTTP requests
- Manages CRUD operations
- Routes definition
- Data validation

### 3. JSON Storage
- `posts.json`: Blog post data
- `customization.json`: Blog settings

### 4. Static Files
- Image uploads
- CSS stylesheets
- Located in `/static`

## Data Flow

1. User Actions → Web Interface
2. Web Interface → Flask Backend
3. Flask Backend → JSON Storage
4. JSON Storage → Flask Backend
5. Flask Backend → Web Interface
