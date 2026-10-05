from app import create_app

app = create_app()

if __name__ == "__main__":
    import os
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    port = int(os.environ.get('PORT', 5002))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)