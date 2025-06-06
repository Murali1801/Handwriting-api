from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
from demo import Hand
import tempfile
import os

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    text = data.get('text', '')
    style = int(data.get('style', 9))
    bias = float(data.get('bias', 0.75))

    if not text:
        return jsonify({'error': 'Text is required'}), 400

    lines = text.split('\n')
    biases = [bias for _ in lines]
    styles = [style for _ in lines]
    stroke_colors = ['black' for _ in lines]
    stroke_widths = [1 for _ in lines]

    hand = Hand()
    # Use a temporary file for the SVG
    with tempfile.NamedTemporaryFile(delete=False, suffix='.svg') as tmp:
        filename = tmp.name
    hand.write(
        filename=filename,
        lines=lines,
        biases=biases,
        styles=styles,
        stroke_colors=stroke_colors,
        stroke_widths=stroke_widths
    )
    # Return the SVG file
    response = send_file(filename, mimetype='image/svg+xml')
    # Clean up the temp file after sending
    @response.call_on_close
    def cleanup():
        os.remove(filename)
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 