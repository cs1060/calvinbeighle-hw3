from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
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
CORS(app)  # Enable CORS for all routes

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ORGANIZED_FOLDER'] = 'organized'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'docx', 'csv'}
SUPPORTED_IMAGES = {'.png', '.jpg', '.jpeg'}
SUPPORTED_DOCS = {'.pdf', '.docx', '.csv'}

# Initialize OpenAI client with API key from .env
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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
    """Analyze document content using OpenAI API to extract topics and themes."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """You are a document analyzer. Analyze the content and suggest appropriate categorization. 
                Rules:
                1. Response must be valid JSON
                2. Include:
                   - 'category' (broad category like 'Education', 'Language', 'Mathematics', 'Personal')
                   - 'subcategory' (general grouping like 'Assignments', 'Course_Materials', 'Exercises')
                   - 'keywords' (list of 3-5 key terms found in content)
                3. Use broad, inclusive categories to group related content together
                4. Similar content should be grouped in the same subcategory
                5. Avoid overly specific categorization"""},
                {"role": "user", "content": f"Analyze this text and suggest a broad category for grouping similar documents: {text[:10000]}"}
            ],
            response_format={ "type": "json_object" }
        )
        result = json.loads(response.choices[0].message.content)
        print(f"AI Analysis result: {result}")  # Debug logging
        return result
    except Exception as e:
        print(f"Error analyzing document: {str(e)}")
        return {
            "category": "Uncategorized",
            "subcategory": "Other",
            "keywords": []
        }

def organize_files(uploaded_files):
    """Organize files based on type and content similarity."""
    org_base = app.config['ORGANIZED_FOLDER']
    os.makedirs(os.path.join(org_base, "Images"), exist_ok=True)
    os.makedirs(os.path.join(org_base, "Documents"), exist_ok=True)
    os.makedirs(os.path.join(org_base, "Other"), exist_ok=True)

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

    # Process and group documents
    document_analyses = {}
    for doc in documents:
        content = extract_words_from_file(doc)
        if content.strip():
            analysis = analyze_document_content(content)
            category = analysis['category'].replace(' ', '_')
            subcategory = analysis['subcategory'].replace(' ', '_')
            document_analyses[doc] = {
                'category': category,
                'subcategory': subcategory,
                'keywords': analysis['keywords']
            }
        else:
            document_analyses[doc] = {
                'category': 'Uncategorized',
                'subcategory': 'Other',
                'keywords': []
            }

    # Group documents by category and subcategory
    organized_folders = defaultdict(lambda: defaultdict(list))
    for doc, analysis in document_analyses.items():
        organized_folders[analysis['category']][analysis['subcategory']].append(doc)

    # Create folders and move documents
    folder_structure = {}
    for category, subcategories in organized_folders.items():
        folder_structure[category] = []
        for subcategory, docs in subcategories.items():
            if docs:  # Only create folders that have documents
                folder_path = os.path.join(org_base, "Documents", category, subcategory)
                os.makedirs(folder_path, exist_ok=True)
                folder_structure[category].append(subcategory)
                
                for doc in docs:
                    filename = os.path.basename(doc)
                    shutil.move(doc, os.path.join(folder_path, filename))

    # Move other files
    for other in others:
        filename = os.path.basename(other)
        shutil.move(other, os.path.join(org_base, "Other", filename))

    return {
        "images": len(images),
        "documents": len(documents),
        "others": len(others),
        "folder_structure": folder_structure
    }

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

if __name__ == '__main__':
    app.run(debug=True) 