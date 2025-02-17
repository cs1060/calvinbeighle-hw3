import os
import io
import pytest
from app import app

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

def test_index_page(client):
    """Test if the index page loads correctly"""
    response = client.get('/')
    assert response.status_code == 200

def test_upload_no_files(client):
    """Test upload endpoint with no files"""
    response = client.post('/upload')
    assert response.status_code == 400
    assert b'No files uploaded' in response.data

def test_upload_with_file(client):
    """Test upload endpoint with a test file"""
    test_file_content = b'Test content'
    data = {
        'files[]': (io.BytesIO(test_file_content), 'test.txt')
    }
    response = client.post('/upload', data=data)
    assert response.status_code == 400  # Should fail because .txt is not allowed

def test_unimplemented_features(client):
    """Test endpoints that are marked as not implemented"""
    response = client.get('/preview/test.pdf')
    assert response.status_code == 501
    assert b'not implemented yet' in response.data

    response = client.get('/download/test.pdf')
    assert response.status_code == 501
    assert b'not implemented yet' in response.data