#!/usr/bin/env python3
"""
Static site generator for Netlify deployment
Converts Flask app to static HTML files
"""

import os
import shutil
from app import create_app
from flask import url_for

def build_static_site():
    """Generate static HTML files from Flask app"""
    
    app = create_app()
    
    # Create dist directory
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    os.makedirs('dist')
    
    # Copy static files
    if os.path.exists('app/static'):
        shutil.copytree('app/static', 'dist/static')
    
    with app.app_context():
        # Generate main pages
        pages = [
            ('/', 'index.html'),
            ('/auth/login', 'login.html'),
            ('/auth/register', 'register.html'),
        ]
        
        for route, filename in pages:
            try:
                with app.test_client() as client:
                    response = client.get(route)
                    if response.status_code == 200:
                        with open(f'dist/{filename}', 'w', encoding='utf-8') as f:
                            f.write(response.get_data(as_text=True))
                        print(f"Generated: {filename}")
            except Exception as e:
                print(f"Error generating {filename}: {e}")
    
    print("Static site build complete!")

if __name__ == '__main__':
    build_static_site()
