document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const selectButton = document.getElementById('selectButton');
    const fileList = document.getElementById('fileList');
    const message = document.getElementById('message');

    selectButton.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#007bff';
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#ccc';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#ccc';
        handleFiles(e.dataTransfer.files);
    });

    function handleFiles(files) {
        const formData = new FormData();
        
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

        message.className = 'info';
        message.textContent = 'Uploading files...';

        fetch('/upload', {
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
                Object.entries(data.stats.folder_structure).forEach(([primary, subfolders]) => {
                    statsMessage += `${primary}/\n`;
                    subfolders.forEach(sub => {
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