import os
import sys
from flask import Flask, render_template, request, send_file, abort
from werkzeug.utils import secure_filename

# Ensure current directory is in module search path for pdf_sorter import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdf_sorter import sort_pdf_by_ocr

# Initialize Flask app with explicit templates folder
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
)

# Configuration
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['SORTED_FOLDER'] = os.path.join(os.getcwd(), 'sorted')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB limit
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure upload and sorted directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SORTED_FOLDER'], exist_ok=True)

# Utility

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'pdfFile' not in request.files:
        abort(400, 'No file part')
    file = request.files['pdfFile']
    raw_filename = file.filename or ''
    if not raw_filename.strip():
        abort(400, 'No selected file')
    if not allowed_file(raw_filename):
        abort(400, 'Invalid file type; please upload a PDF.')

    # Secure and save the uploaded PDF
    filename = secure_filename(raw_filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(input_path)
    except Exception as e:
        abort(500, f"Error saving file: {e}")

    # Define output path
    output_filename = f"sorted_{filename}"
    output_path = os.path.join(app.config['SORTED_FOLDER'], output_filename)

    # Perform sorting
    try:
        sort_pdf_by_ocr(input_path, output_path)
    except Exception as e:
        abort(500, f"Error processing PDF: {e}")

    # Send the sorted PDF back to the user
    try:
        return send_file(output_path, as_attachment=True, download_name=output_filename)
    except Exception as e:
        abort(500, f"Error sending file: {e}")

if __name__ == '__main__':
    # Run development server
    app.run(debug=True)
