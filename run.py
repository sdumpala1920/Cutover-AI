"""Entry point: python run.py"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug=True gives auto-reload during content/curriculum editing.
    app.run(host="127.0.0.1", port=5000, debug=True)
