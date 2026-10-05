#!/usr/bin/env python3
"""
Build script for Cloudflare Pages deployment
Generates static files with API integration
"""

import os
import shutil
import json
from pathlib import Path

def build_for_cloudflare():
    """Build static site for Cloudflare Pages"""
    
    print("🚀 Building for Cloudflare Pages...")
    
    # Create build directory
    build_dir = Path('dist')
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir()
    
    # Copy static assets
    static_src = Path('app/static')
    if static_src.exists():
        static_dest = build_dir / 'static'
        shutil.copytree(static_src, static_dest)
        print("✅ Copied static assets")
    
    # Copy Cloudflare configuration
    config_files = ['_headers', '_redirects']
    for config_file in config_files:
        if Path(config_file).exists():
            shutil.copy(config_file, build_dir)
            print(f"✅ Copied {config_file}")
    
    # Copy functions
    functions_src = Path('functions')
    if functions_src.exists():
        functions_dest = build_dir / 'functions'
        shutil.copytree(functions_src, functions_dest)
        print("✅ Copied Cloudflare Functions")
    
    # Generate main HTML file
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spoof Suite Marketplace</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div id="app">
        <h1>🚀 Spoof Suite Marketplace</h1>
        <p>Loading marketplace data...</p>
        <div id="data-container"></div>
    </div>
    
    <script>
        // Fetch data from Cloudflare Function
        async function loadData() {
            try {
                const response = await fetch('/api/data');
                const data = await response.json();
                
                document.getElementById('data-container').innerHTML = `
                    <div class="stats">
                        <div class="stat-card">
                            <h3>💳 Credit Cards</h3>
                            <p>${data.credit_cards}</p>
                        </div>
                        <div class="stat-card">
                            <h3>💰 Debit Cards</h3>
                            <p>${data.debit_cards}</p>
                        </div>
                        <div class="stat-card">
                            <h3>🏦 Plaid Logs</h3>
                            <p>${data.plaid_logs}</p>
                        </div>
                        <div class="stat-card">
                            <h3>👤 Fullz</h3>
                            <p>${data.fullz_count}</p>
                        </div>
                    </div>
                    
                    <div class="notifications">
                        <h3>📢 Alerts</h3>
                        ${data.notifications.map(note => `<div class="alert">${note}</div>`).join('')}
                    </div>
                    
                    <div class="bins">
                        <h3>🔢 Latest BINs</h3>
                        <table>
                            <tr><th>BIN</th><th>Type</th><th>Bank</th><th>Country</th></tr>
                            ${data.bins.map(bin => `
                                <tr>
                                    <td>${bin.bin}</td>
                                    <td>${bin.type}</td>
                                    <td>${bin.bank}</td>
                                    <td>${bin.country}</td>
                                </tr>
                            `).join('')}
                        </table>
                    </div>
                `;
            } catch (error) {
                console.error('Error loading data:', error);
                document.getElementById('data-container').innerHTML = '<p>Error loading marketplace data</p>';
            }
        }
        
        // Load data when page loads
        document.addEventListener('DOMContentLoaded', loadData);
    </script>
    
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #0f172a; color: #e2e8f0; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-card { background: #1e293b; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #10b981; }
        .stat-card h3 { margin: 0 0 10px 0; color: #10b981; }
        .stat-card p { font-size: 2rem; font-weight: bold; margin: 0; }
        .notifications, .bins { margin: 30px 0; }
        .alert { background: rgba(16, 185, 129, 0.1); border-left: 3px solid #10b981; padding: 10px; margin: 5px 0; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #334155; padding: 10px; text-align: left; }
        th { background: #1e293b; color: #10b981; }
        h1 { text-align: center; color: #10b981; }
        h3 { color: #10b981; }
    </style>
</body>
</html>"""
    
    with open(build_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Generated index.html")
    print("🎉 Cloudflare Pages build complete!")
    print(f"📁 Build output: {build_dir.absolute()}")

if __name__ == '__main__':
    build_for_cloudflare()
