from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
from demo import Hand
import tempfile
import os
import logging
import traceback
import time

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
    start_time = time.time()
    try:
        data = request.get_json()
        text = data.get('text', '')
        style = int(data.get('style', 9))
        bias = float(data.get('bias', 0.75))
        line_spacing = float(data.get('line_spacing', 0.75))
        font_size = float(data.get('font_size', 1.0))
        text_align = data.get('text_align', 'center')

        if not text:
            return jsonify({'error': 'Text is required'}), 400

        logger.info(f"Generating handwriting for text: {text[:50]}...")

        lines = []
        current_line = ""
        words = text.split()
        for word in words:
            if len(current_line) + len(word) + 1 <= 75:
                current_line += (word + " ")
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())

        logger.info(f"Split text into {len(lines)} lines")

        biases = [bias for _ in lines]
        styles = [style for _ in lines]
        stroke_colors = ['black' for _ in lines]
        stroke_widths = [1 for _ in lines]

        hand = Hand()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.svg') as tmp:
            filename = tmp.name
            logger.info("Starting handwriting generation...")
            hand.write(
                filename=filename,
                lines=lines,
                biases=biases,
                styles=styles,
                stroke_colors=stroke_colors,
                stroke_widths=stroke_widths,
                line_spacing=line_spacing,
                font_size=font_size,
                text_align=text_align
            )
            logger.info("Handwriting generation completed")

        response = send_file(filename, mimetype='image/svg+xml')
        @response.call_on_close
        def cleanup():
            try:
                os.remove(filename)
            except Exception as e:
                logger.error(f"Error cleaning up temp file: {str(e)}")
        generation_time = time.time() - start_time
        logger.info(f"Total generation time: {generation_time:.2f} seconds")
        return response
    except Exception as e:
        logger.error(f"Error generating handwriting: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Error generating handwriting',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 