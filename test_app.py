import os
import io
import json
import pytest
from app import app, analyze_document_content, extract_words_from_file
from unittest.mock import patch, MagicMock

# Add this patch to mock the OpenAI client for all tests
@pytest.fixture(autouse=True)
def mock_openai_env(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'test_key')

@pytest.fixture
def mock_get_openai_client():
    with patch('app.get_openai_client') as mock:
        client = MagicMock()
        mock.return_value = client
        yield client

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = 'test_uploads'
    app.config['ORGANIZED_FOLDER'] = 'test_organized'
    
    # Create test directories
    os.makedirs('test_uploads', exist_ok=True)
    os.makedirs('test_organized', exist_ok=True)
    
    with app.test_client() as client:
        yield client
        
    # Cleanup after tests
    for folder in ['test_uploads', 'test_organized']:
        if os.path.exists(folder):
            for root, dirs, files in os.walk(folder, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(folder)

@pytest.fixture
def mock_openai_response():
    # Update to match new response format
    return {
        "group": "Reports"  # Simplified response with just the group name
    }

def test_index_page(client):
    """Test if the index page loads correctly"""
    response = client.get('/')
    assert response.status_code == 200

def test_upload_no_files(client):
    """Test upload endpoint with no files"""
    response = client.post('/upload')
    assert response.status_code == 400
    assert b'No files uploaded' in response.data

def test_upload_invalid_file_type(client):
    """Test upload with invalid file type"""
    data = {
        'files[]': (io.BytesIO(b'test content'), 'test.txt')
    }
    response = client.post('/upload', data=data)
    assert response.status_code == 400
    assert b'File type not allowed' in response.data

@patch('app.OpenAI')
def test_upload_valid_files(mock_openai, client, mock_openai_response):
    """Test upload with valid files"""
    # Mock OpenAI client response
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = json.dumps(mock_openai_response)
    mock_openai.return_value.chat.completions.create.return_value = mock_completion

    # Create test files
    pdf_content = io.BytesIO(b'%PDF-1.4 test pdf content')
    image_content = io.BytesIO(b'fake image content')
    
    data = {
        'files[]': [
            (pdf_content, 'test.pdf'),
            (image_content, 'test.jpg')
        ]
    }
    
    response = client.post('/upload', data=data)
    assert response.status_code == 200
    
    response_data = json.loads(response.data)
    assert 'message' in response_data
    assert 'stats' in response_data
    assert response_data['stats']['images'] == 1
    assert response_data['stats']['documents'] == 1

def test_unimplemented_features(client):
    """Test endpoints that are marked as not implemented"""
    response = client.get('/preview/test.pdf')
    assert response.status_code == 501
    assert b'not implemented yet' in response.data

    response = client.get('/download/test.pdf')
    assert response.status_code == 501
    assert b'not implemented yet' in response.data

@patch('app.OpenAI')
def test_analyze_document_content(mock_openai, mock_openai_response):
    """Test document content analysis"""
    # Mock OpenAI client response
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = json.dumps(mock_openai_response)
    mock_openai.return_value.chat.completions.create.return_value = mock_completion

    result = analyze_document_content("Test document content")
    assert result == "Reports"  # Now expecting just the group name string

def test_analyze_document_content_error():
    """Test document analysis error handling"""
    result = analyze_document_content(None)
    assert result == "Other"  # Now expecting just the "Other" string

def test_extract_words_from_file_invalid():
    """Test text extraction from invalid file"""
    result = extract_words_from_file('nonexistent.pdf')
    assert result == ""

def test_error_handler(client):
    """Test 500 error handler"""
    with patch('app.organize_files', side_effect=Exception('Test error')):
        data = {
            'files[]': (io.BytesIO(b'test content'), 'test.pdf')
        }
        response = client.post('/upload', data=data)
        assert response.status_code == 500
        assert b'Error organizing files' in response.data