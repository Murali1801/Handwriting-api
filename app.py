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

        logger.info(f"Generating handwriting for text: {text[:50]}...")
        
        # Split text into lines of 75 characters each with word wrapping
        lines = []
        current_line = ""
        words = text.split()
        
        for word in words:
            # If adding this word would exceed the line limit
            if len(current_line) + len(word) + 1 > 75:  # +1 for space
                if current_line:  # If there's content in current line
                    lines.append(current_line)
                    current_line = word
                else:  # If current line is empty, word is too long
                    # Split long word into chunks of 75
                    for i in range(0, len(word), 75):
                        chunk = word[i:i+75]
                        lines.append(chunk)
                    current_line = ""
            else:
                if current_line:  # Add space if not first word
                    current_line += " "
                current_line += word
        
        # Add the last line if it's not empty
        if current_line:
            lines.append(current_line)
        
        # If no lines were created (empty text), return error
        if not lines:
            return jsonify({'error': 'No valid text to generate'}), 400

        biases = [bias for _ in lines]
        styles = [style for _ in lines]
        stroke_colors = ['black' for _ in lines]
        stroke_widths = [1 for _ in lines]

        hand = Hand()
        # Use a temporary file for the SVG
        with tempfile.NamedTemporaryFile(delete=False, suffix='.svg') as tmp:
            filename = tmp.name
        
        logger.info(f"Starting handwriting generation for {len(lines)} lines...")
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