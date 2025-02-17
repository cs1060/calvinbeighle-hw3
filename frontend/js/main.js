const API_URL = 'http://localhost:5000';  // Local development backend URL

document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const selectButton = document.getElementById('selectButton');
    const fileList = document.getElementById('fileList');
    const message = document.getElementById('message');

    // Handle file selection button
    selectButton.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle file input change
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    // Handle drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    function handleFiles(files) {
        const formData = new FormData();
        
        // Clear any previous messages
        message.textContent = '';
        
        if (!files || files.length === 0) {
            message.className = 'error';
            message.textContent = 'Please select files to upload';
            return;
        }
        
        for (let file of files) {
            formData.append('files[]', file);
        }

        fileList.innerHTML = Array.from(files)
            .map(file => `<div>${file.name}</div>`)
            .join('');

        // Add loading indication
        message.className = 'info';
        message.textContent = 'Uploading and organizing files...';

        fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            message.className = 'success';
            let statsMessage = `${data.message}\n`;
            statsMessage += `Images: ${data.stats.images}, Documents: ${data.stats.documents}, Others: ${data.stats.others}\n\n`;
            
            if (data.stats.folder_structure) {
                statsMessage += 'Organized Structure:\n';
                Object.entries(data.stats.folder_structure).forEach(([category, subcategories]) => {
                    statsMessage += `${category}/\n`;
                    subcategories.forEach(sub => {
                        statsMessage += `  └── ${sub}/\n`;
                    });
                });
            }
            
            message.textContent = statsMessage;
        })
        .catch(error => {
            message.className = 'error';
            message.textContent = `Error: ${error.message}`;
        });
    }
}); 