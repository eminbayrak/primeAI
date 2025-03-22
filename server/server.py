from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
import numpy as np
import cv2
import os
import time
import traceback
import re  # Add missing import for regular expressions
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from claude_service import claude_service

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize API key from environment variable
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
if CLAUDE_API_KEY:
    claude_service.init_api_client(CLAUDE_API_KEY)

# Initialize the OCR reader cache
readers = {}

def get_reader(lang, gpu=False, network_config=None):
    """Get or create an EasyOCR reader for the specified language."""
    try:
        cache_key = f"{lang}_{gpu}_{network_config}"
        
        if cache_key not in readers:
            # Map frontend language codes to EasyOCR language codes
            lang_mapping = {
                'eng': ['en'],
                'spa': ['es'],
                'fra': ['fr'],
                'deu': ['de'],
                'chi_sim': ['ch_sim'],
                'jpn': ['ja'],
                'kor': ['ko'],
                'rus': ['ru']
            }
            
            # Default to English if language not supported
            ocr_lang = lang_mapping.get(lang, ['en'])
            
            print(f"Initializing EasyOCR reader for language: {ocr_lang}")
            
            # Create reader with specific configuration if provided
            if network_config == 'fast':
                # Use a simpler model for faster processing
                readers[cache_key] = easyocr.Reader(ocr_lang, gpu=gpu, quantize=True, model_storage_directory='./models')
            elif network_config == 'accurate':
                # Use the full model for best accuracy
                readers[cache_key] = easyocr.Reader(ocr_lang, gpu=gpu, quantize=False, 
                                                model_storage_directory='./models')
            else:
                # Default configuration
                readers[cache_key] = easyocr.Reader(ocr_lang, gpu=gpu, model_storage_directory='./models')
            
            print(f"Successfully initialized reader for {lang}")
        
        return readers[cache_key]
    except Exception as e:
        print(f"Error creating EasyOCR reader: {str(e)}")
        print(traceback.format_exc())
        raise

def preprocess_image(img, preprocessing=None):
    """Apply preprocessing to an image."""
    if preprocessing is None:
        return img
    
    processed = img.copy()
    
    if 'grayscale' in preprocessing:
        processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
        processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
    
    if 'contrast' in preprocessing:
        # Convert to LAB color space where L is the luminance
        lab = cv2.cvtColor(processed, cv2.COLOR_BGR2LAB)
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        # Convert back to BGR color space
        processed = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    if 'sharpen' in preprocessing:
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        processed = cv2.filter2D(processed, -1, kernel)
    
    return processed

@app.route('/ocr', methods=['POST'])
def perform_ocr():
    temp_filepath = None
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Get parameters from request
        lang = request.form.get('language', 'eng')
        quality = request.form.get('quality', 'standard')  # fast, standard, or best
        preprocessing = request.form.getlist('preprocessing')  # List of preprocessing steps
        preserve_layout = request.form.get('preserve_layout', 'true').lower() == 'true'  # New parameter
        
        print(f"OCR request: lang={lang}, quality={quality}, preprocessing={preprocessing}, preserve_layout={preserve_layout}")
        
        # Map quality to network config
        network_config = None
        if quality == 'fast':
            network_config = 'fast'
        elif quality == 'best':
            network_config = 'accurate'
        
        # Determine if GPU should be used (based on environment variable)
        use_gpu = os.environ.get('USE_GPU', '0').lower() in ('true', '1', 't')
        
        # Create temp directory if it doesn't exist
        if not os.path.exists('temp'):
            os.makedirs('temp')
        
        # Save file temporarily
        filename = secure_filename(f"{int(time.time())}_{file.filename}")
        temp_filepath = os.path.join('temp', filename)
        file.save(temp_filepath)
        
        print(f"Image saved to {temp_filepath}")
        
        # Read image using OpenCV
        img = cv2.imread(temp_filepath)
        if img is None:
            return jsonify({'error': f'Failed to read image at {temp_filepath}'}), 400
            
        # Apply preprocessing if requested
        if preprocessing:
            img = preprocess_image(img, preprocessing)
        
        # Get the EasyOCR reader with appropriate configuration
        reader = get_reader(lang, gpu=use_gpu, network_config=network_config)
        
        # Determine recognition parameters based on quality
        paragraph = quality != 'fast'  # Group text into paragraphs for standard and best
        detail = 0 if quality == 'fast' else 1  # Level of detection detail
        
        print(f"Starting OCR with paragraph={paragraph}, detail={detail}")
        
        # Perform OCR
        result = reader.readtext(img, paragraph=paragraph, detail=detail)
        
        print(f"OCR completed with {len(result)} text regions detected")
        
        # Format the results based on whether layout preservation is enabled
        if preserve_layout and len(result) > 1:
            # Improved spatial analysis for better layout preservation
            
            # Sort boxes by vertical position (top to bottom)
            boxes_with_positions = []
            for box in result:
                # Each box contains coordinates: [[top-left, top-right, bottom-right, bottom-left], text, confidence]
                if len(box) >= 2:
                    # Get the bounding box center Y position and height
                    top_y = min(point[1] for point in box[0])
                    bottom_y = max(point[1] for point in box[0])
                    height = bottom_y - top_y
                    center_y = top_y + height/2
                    left_x = min(point[0] for point in box[0])
                    
                    boxes_with_positions.append({
                        'box': box,
                        'top': top_y,
                        'bottom': bottom_y,
                        'center_y': center_y,
                        'height': height,
                        'left': left_x,
                        'text': box[1]
                    })
            
            # Sort boxes by top Y position
            sorted_boxes = sorted(boxes_with_positions, key=lambda x: x['top'])
            
            # Group boxes into lines based on overlap
            lines = []
            current_line = [sorted_boxes[0]]
            line_bottom = sorted_boxes[0]['bottom']
            
            for i in range(1, len(sorted_boxes)):
                current_box = sorted_boxes[i]
                # If this box's top is above the previous line's bottom or they overlap significantly,
                # add it to the current line
                vertical_overlap = min(line_bottom, current_box['bottom']) - current_box['top']
                overlap_ratio = vertical_overlap / current_box['height'] if current_box['height'] > 0 else 0
                
                if overlap_ratio > 0.25:  # They belong to the same line if 25% overlap
                    current_line.append(current_box)
                    line_bottom = max(line_bottom, current_box['bottom'])
                else:
                    # Start a new line
                    lines.append(current_line)
                    current_line = [current_box]
                    line_bottom = current_box['bottom']
            
            # Add the last line
            if current_line:
                lines.append(current_line)
            
            # For each line, sort elements from left to right and join with spaces
            text_lines = []
            for line in lines:
                # Sort by left x-coordinate
                sorted_line = sorted(line, key=lambda x: x['left'])
                
                # Calculate average character width to determine spacing
                avg_char_width = 0
                total_width = 0
                total_chars = 0
                
                for box in sorted_line:
                    width = max(p[0] for p in box['box'][0]) - min(p[0] for p in box['box'][0])
                    chars = len(box['text'])
                    if chars > 0:
                        total_width += width
                        total_chars += chars
                
                if total_chars > 0:
                    avg_char_width = total_width / total_chars
                
                # Join text with appropriate spacing
                line_text = ""
                last_right = 0
                
                for i, box in enumerate(sorted_line):
                    if i > 0:
                        # Calculate gap between this box and previous one
                        left = min(p[0] for p in box['box'][0])
                        gap = left - last_right
                        
                        # Add spaces based on gap size
                        spaces = int(gap / (avg_char_width * 0.7)) if avg_char_width > 0 else 1
                        line_text += " " * max(1, min(spaces, 8))  # Limit to reasonable number
                    
                    line_text += box['text']
                    last_right = max(p[0] for p in box['box'][0])
                
                text_lines.append(line_text)
            
            # Join lines with newlines, preserving paragraph structure
            text = "\n".join(text_lines)
            
            # Preserve multiple newlines for paragraph separation
            text = re.sub(r'\n{3,}', '\n\n', text)
            
        elif paragraph:
            # In paragraph mode, join the text blocks with spaces
            text = " ".join([block[1] for block in result])
        else:
            # In non-paragraph mode, add spaces and line breaks
            text = ""
            for detection in result:
                text += detection[1] + " "
                if detection[1].endswith(('.', '?', '!')):
                    text += "\n"
        
        # Calculate average confidence - safely handle different result structures
        try:
            # Try to extract confidence scores if they exist
            confidences = []
            for box in result:
                if len(box) > 2 and box[2] is not None:  # Check if confidence exists
                    confidences.append(box[2])
            
            # Calculate average confidence if we have valid scores
            confidence = sum(confidences) / len(confidences) if confidences else 0.5
            print(f"Calculated confidence: {confidence}")
        except Exception as e:
            # Fallback to a medium confidence if calculation fails
            print(f"Warning: Could not calculate confidence: {str(e)}")
            confidence = 0.5
        
        # Clean up
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        
        return jsonify({
            'text': text.strip(),
            'confidence': confidence,
            'words': len(result),
            'engine': 'easyocr',
            'quality': quality
        })
    
    except Exception as e:
        # Print detailed error information
        print(f"Error during OCR processing: {str(e)}")
        print(traceback.format_exc())
        
        # Clean up on error
        if temp_filepath and os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 
        'version': '1.0.0',
        'gpu_available': os.environ.get('USE_GPU', '0').lower() in ('true', '1', 't')
    })

@app.route('/info', methods=['GET'])
def server_info():
    return jsonify({
        'supported_languages': {
            'eng': 'English',
            'spa': 'Spanish',
            'fra': 'French',
            'deu': 'German',
            'chi_sim': 'Chinese Simplified',
            'jpn': 'Japanese',
            'kor': 'Korean',
            'rus': 'Russian'
        },
        'preprocessing_options': ['grayscale', 'contrast', 'sharpen'],
        'quality_options': ['fast', 'standard', 'best'],
        'version': '1.0.0'
    })

# Chat-related endpoints
@app.route('/chat/health', methods=['GET'])
def chat_health():
    """Check the status of the chat service"""
    api_available = claude_service.init_api_client(CLAUDE_API_KEY)
    local_available = claude_service.load_local_model() if not claude_service.model_loaded else True
    
    return jsonify({
        'api_available': api_available,
        'local_available': local_available,
        'status': 'healthy' if api_available or local_available else 'degraded'
    })

@app.route('/chat/message', methods=['POST'])
def chat_message():
    """Process a chat message and return a response"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        messages = data.get('messages', [])
        api_key = data.get('api_key')
        use_local = data.get('use_local', False)
        
        # If API key is provided in the request, initialize the client with it
        if api_key and not use_local:
            claude_service.init_api_client(api_key)
        
        # Generate response
        response, metadata = claude_service.generate_response(messages, use_local=use_local)
        
        return jsonify({
            'message': response,
            'metadata': metadata
        })
        
    except Exception as e:
        print(f"Error in chat message endpoint: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create needed directories
    for directory in ['temp', 'models']:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting server on port {port}...")
    print(f"GPU enabled: {os.environ.get('USE_GPU', '0').lower() in ('true', '1', 't')}")
    print(f"Claude API available: {CLAUDE_API_KEY is not None}")
    
    # Make sure to capture all output
    import sys
    sys.stdout.flush()
    
    app.run(debug=True, host='0.0.0.0', port=port)
