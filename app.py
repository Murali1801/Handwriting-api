from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
from demo import Hand
import tempfile
import os
import logging
import traceback

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        text = data.get('text', '')
        style = int(data.get('style', 9))
        bias = float(data.get('bias', 0.75))

        if not text:
            return jsonify({'error': 'Text is required'}), 400

        # Check total character limit
        if len(text) > 500:
            return jsonify({
                'error': 'Text exceeds maximum length of 500 characters',
                'details': f'Current length: {len(text)} characters'
            }), 400

        logger.info(f"Generating handwriting for text: {text[:50]}...")
        
        # Split text into lines of 75 characters each
        lines = []
        current_line = ""
        for char in text:
            if len(current_line) >= 75:
                lines.append(current_line)
                current_line = char
            else:
                current_line += char
        if current_line:  # Add the last line if it's not empty
            lines.append(current_line)
        
        # Ensure we don't exceed the model's line limit
        if len(lines) > 7:  # 500/75 ≈ 6.67, so 7 lines max
            return jsonify({
                'error': 'Text generates too many lines',
                'details': f'Maximum 7 lines allowed, got {len(lines)} lines'
            }), 400

        biases = [bias for _ in lines]
        styles = [style for _ in lines]
        stroke_colors = ['black' for _ in lines]
        stroke_widths = [1 for _ in lines]

        hand = Hand()
        # Use a temporary file for the SVG
        with tempfile.NamedTemporaryFile(delete=False, suffix='.svg') as tmp:
            filename = tmp.name
        
        logger.info("Starting handwriting generation...")
        hand.write(
            filename=filename,
            lines=lines,
            biases=biases,
            styles=styles,
            stroke_colors=stroke_colors,
            stroke_widths=stroke_widths
        )
        logger.info("Handwriting generation completed")

        # Read the SVG file content
        with open(filename, 'r') as f:
            svg_content = f.read()

        # Clean up the temp file
        try:
            os.remove(filename)
        except Exception as e:
            logger.error(f"Error cleaning up temp file: {str(e)}")

        return jsonify({'svg': svg_content})

    except Exception as e:
        logger.error(f"Error generating handwriting: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Error generating handwriting',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 