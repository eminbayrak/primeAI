# Image to Text Converter

A Vue.js application that converts images to text using OCR (Optical Character Recognition). This application supports both browser-based OCR with Tesseract.js and server-based OCR with EasyOCR for improved results.

## Features

- Paste screenshots directly from clipboard
- Upload images from local storage
- Image preprocessing options (grayscale, contrast enhancement, sharpening)
- Multiple OCR engines:
  - Tesseract.js (runs in browser, no setup required)
  - EasyOCR (Python backend, better accuracy)
- Text post-processing for improved results
- Multiple language support
- Copy extracted text to clipboard
- Confidence score display

## Project Setup

### Frontend Setup

```bash
# Install dependencies
npm install

# Run development server
npm run serve

# Build for production
npm run build
```

### EasyOCR Backend Setup

The EasyOCR backend requires Python 3.6+ and several dependencies.

#### Option 1: Manual Setup with Virtual Environment (Recommended)

1. Create and activate a virtual environment:

```bash
# Navigate to the server directory
cd server

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

2. Install dependencies:

```bash
# Make sure your virtual environment is activated (you should see (venv) in your terminal)
pip install -r requirements.txt
```

3. Run the server:

```bash
python server.py
```

4. When you're done, deactivate the virtual environment:

```bash
deactivate
```

The server will start on http://localhost:5000.

#### Option 2: Using the Setup Script

We've provided a convenience script for Linux/macOS users:

```bash
cd server
chmod +x setup.sh
./setup.sh
```

#### Option 3: Docker Setup

1. Build the Docker image:

```bash
cd server
docker build -t easyocr-api .
```

2. Run the container:

```bash
docker run -p 5000:5000 easyocr-api
```

## Usage

1. Open the application in a browser
2. Paste an image from clipboard or upload an image file
3. Select the OCR engine (Tesseract.js or EasyOCR)
4. Select the language and recognition quality
5. Click "Convert to Text"
6. View the extracted text and copy it to clipboard if needed

## Components

- **Frontend**: Vue.js 3 with TypeScript
- **Client-side OCR**: Tesseract.js
- **Server-side OCR**: EasyOCR with Flask API
- **Text Processing**: Custom post-processing algorithms

## Notes

- EasyOCR provides better accuracy but requires server-side processing
- For the best results with challenging images:
  1. Use the image preprocessing tools (e.g., increase contrast for low-contrast images)
  2. Select the appropriate language
  3. Use the "Best Quality" setting for more accurate but slower processing
