# Typo Blog App

Typo is a minimalist blog application for short notes, ideas, and everyday writing. Built with Flask and using JSON for data persistence, it provides an intuitive interface for creating and managing blog posts with image support.

## Documentation

- [SDLC Documentation](docs/SDLC.md)
- [Architecture Overview](docs/architecture.md)
- [Requirements Documentation](docs/requirements.md)
- [Planning Documentation](docs/planning.md)

## Features

- Create, read, update, and delete blog posts
- Image upload support
- JSON-based data persistence
- Clean and minimal user interface
- Customizable blog settings

## Prerequisites

- Python 3.7+
- pip (Python package manager)
- Virtual environment (recommended)

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/sofiasanjose/typo-blog-app.git
   cd typo-blog-app
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   cd typo
   python app.py
   ```

5. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
typo/
├── app.py           # Main application file
├── posts.json      # Data storage
├── static/         # Static files (CSS, uploads)
└── templates/      # HTML templates
```
