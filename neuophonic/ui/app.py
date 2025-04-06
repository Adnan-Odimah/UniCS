# ui/app.py

from flask import Flask, jsonify, render_template
import threading
from flask_cors import CORS
import time
import main  # import your main.py module

app = Flask(__name__)

CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response')
def get_response():
    # Return the latest text response as JSON
    return jsonify({'text_response': main.latest_text_response})

def run_main_loop():
    import asyncio
    asyncio.run(main.main())

if __name__ == '__main__':
    # Start the main process in a separate thread
    t = threading.Thread(target=run_main_loop)
    t.daemon = True
    t.start()
    
    # Start the Flask web app
    app.run(host='0.0.0.0', port=5000, debug=True)
