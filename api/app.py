from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Flask is running on Vercel!"


from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from docx import Document
import PyPDF2
import csv
import shutil
from openai import OpenAI
import json
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ORGANIZED_FOLDER'] = 'organized'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'docx', 'csv'}
SUPPORTED_IMAGES = {'.png', '.jpg', '.jpeg'} 
SUPPORTED_DOCS = {'.pdf', '.docx', '.csv'}

def get_openai_client():
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables")
    return OpenAI(api_key=api_key)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_words_from_file(filepath):
    """Extract text content from supported document types."""
    try:
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.docx':
            doc = Document(filepath)
            return " ".join([paragraph.text for paragraph in doc.paragraphs])[:10000]
        
        elif ext == '.pdf':
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = " ".join([page.extract_text() for page in reader.pages])
                return text[:10000]
        
        elif ext == '.csv':
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                text = " ".join([" ".join(row) for row in reader])
                return text[:10000]
        
        return ""
    except Exception as e:
        print(f"Error extracting text from {filepath}: {str(e)}")
        return ""

def analyze_document_content(text):
    """Analyze document content using OpenAI API to suggest subject/topic grouping."""
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """You are a document organizer. Based on document content, suggest an academic subject or topic category.
                Rules:
                1. Response must be valid JSON
                2. Include only:
                   - 'subject' (academic subjects like 'Mathematics', 'English', 'History', 'Physics', etc)
                3. Be specific but general enough for categorization
                4. Use standard academic subject names that would make sense in a student's folder structure"""},
                {"role": "user", "content": f"Suggest an academic subject category for this document content: {text[:1000]}"}
            ],
            response_format={ "type": "json_object" }
        )
        result = json.loads(response.choices[0].message.content)
        return result['subject']
    except Exception as e:
        print(f"Error analyzing document: {str(e)}")
        return "Miscellaneous"

def organize_files(uploaded_files):
    """Organize files into subject/topic groups based on type and content."""
    org_base = app.config['ORGANIZED_FOLDER']
    os.makedirs(os.path.join(org_base, "Images"), exist_ok=True)
    os.makedirs(os.path.join(org_base, "Subjects"), exist_ok=True)
    os.makedirs(os.path.join(org_base, "Miscellaneous"), exist_ok=True)

    # Separate files by type
    images = []
    documents = []
    others = []

    for filepath in uploaded_files:
        ext = os.path.splitext(filepath)[1].lower()
        if ext in SUPPORTED_IMAGES:
            images.append(filepath)
        elif ext in SUPPORTED_DOCS:
            documents.append(filepath)
        else:
            others.append(filepath)

    # Move images
    for img in images:
        filename = os.path.basename(img)
        shutil.move(img, os.path.join(org_base, "Images", filename))

    # Process and group documents by subject
    subject_groups = defaultdict(list)
    for doc in documents:
        content = extract_words_from_file(doc)
        if content.strip():
            subject = analyze_document_content(content)
            subject_groups[subject].append(doc)
        else:
            subject_groups["Miscellaneous"].append(doc)

    # Create subject folders and move documents
    folder_structure = {}
    for subject, docs in subject_groups.items():
        if docs:  # Only create folders that have documents
            folder_path = os.path.join(org_base, "Subjects", subject)
            os.makedirs(folder_path, exist_ok=True)
            folder_structure[subject] = []
            
            for doc in docs:
                filename = os.path.basename(doc)
                shutil.move(doc, os.path.join(folder_path, filename))

    # Move other files
    for other in others:
        filename = os.path.basename(other)
        shutil.move(other, os.path.join(org_base, "Miscellaneous", filename))

    return {
        "images": len(images),
        "documents": len(documents),
        "others": len(others),
        "folder_structure": folder_structure
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('files[]')
        if not files:
            return jsonify({'error': 'No files selected'}), 400

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({'error': 'OpenAI API key not configured'}), 500

        # Create necessary directories
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['ORGANIZED_FOLDER'], exist_ok=True)
        
        uploaded_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_files.append(filepath)
            else:
                return jsonify({'error': f'File type not allowed: {file.filename}'}), 400

        try:
            stats = organize_files(uploaded_files)
            return jsonify({
                'message': 'Files organized successfully',
                'stats': stats
            })
        except Exception as e:
            print(f"Error organizing files: {str(e)}")
            # Clean up uploaded files in case of error
            for filepath in uploaded_files:
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except:
                        pass
            return jsonify({'error': f'Error organizing files: {str(e)}'}), 500

    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    """Download organized files (not implemented)"""
    return jsonify({'error': 'Download feature not implemented yet'}), 501

@app.route('/preview/<path:filename>')
def preview_file(filename):
    """Preview file contents (not implemented)"""
    return jsonify({'error': 'Preview feature not implemented yet'}), 501

# Add error handler for 500 errors
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True)