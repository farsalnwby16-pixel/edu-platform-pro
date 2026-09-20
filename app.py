
try:
    
    SOCKETIO_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    SOCKETIO_AVAILABLE = False
    class DummySocketIO:
        def __init__(self, app=None, **kwargs):
            pass
        def on(self, event, *args, **kwargs):
            def decorator(f):
                return f
            return decorator
        def emit(self, *args, **kwargs):
            pass
        def run(self, app, *args, **kwargs):
            app.run(*args, **kwargs)
    SocketIO = DummySocketIO
    def emit(*args, **kwargs):
        pass
    def join_room(*args, **kwargs):
        pass
    def leave_room(*args, **kwargs):
        pass

from flask import Flask, render_template, request, jsonify
try:
    
    SOCKETIO_AVAILABLE = True
except ImportError:
    SocketIO = None
    SOCKETIO_AVAILABLE = False
from groq import Groq
import os

app = Flask(__name__)
 if SOCKETIO_AVAILABLE else None

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "")
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": user_message}],
            model="llama-3.3-70b-versatile"
        )
        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    
