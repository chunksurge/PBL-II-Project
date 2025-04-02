const fileInput = document.getElementById('pdfUpload');
fileInput.addEventListener('change', () => handleFileUpload());

const uploadCard = document.getElementById('uploadCard');
uploadCard.addEventListener('click', () => fileInput.click());

async function handleFileUpload() {
    const file = fileInput.files[0];
    const uploadArea = document.getElementById('uploadArea');
    const uploadIcon = document.getElementById('uploadIcon');
    const uploadTitle = document.getElementById('uploadTitle');
    const uploadSubtitle = document.getElementById('uploadSubtitle');
    const progressSection = document.getElementById('progressSection');
    const progressBar = document.getElementById('progressBar');
    const statusText = document.getElementById('uploadStatus');
    const cardBody = fileInput.closest('.card-body');

    if (!file) {
        return;
    }

    // Hide initial elements and show file name with progress
    uploadIcon.style.display = 'none';
    uploadTitle.textContent = file.name;
    uploadTitle.style.fontSize = '1rem'; // Smaller for file name
    uploadSubtitle.style.display = 'none';
    progressSection.style.display = 'block';
    progressBar.style.width = '0%';
    progressBar.setAttribute('aria-valuenow', 0);
    cardBody.style.pointerEvents = 'none'; // Disable clicking during upload

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/', true);

    // Track upload progress
    xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            progressBar.style.width = percentComplete.toString() + '%';
            progressBar.setAttribute('aria-valuenow', percentComplete)
        }
    };

    // Handle completion
    xhr.onload = () => {
        if (xhr.status === 200) {
            let response = JSON.parse(xhr.responseText);
            
            if (response.file_id) {
                let formData = new FormData();
                formData.append('file_id', response.file_id);
                statusText.innerText = 'Processing PDF...';
                progressBar.style.width = '0%';
                let progressInterval = setInterval(() => {
                    fetch("/", { method: 'POST', body: formData })
                    .then(response => response.json())
                    .then(data => {
                        progressBar.style.width = data.progress.toString() + '%';
                        progressBar.setAttribute('aria-valuenow', data.progress);
                        if (data.progress == 100) {
                            clearInterval(progressInterval);
                            window.location.href = data.redirect_url;
                        }
                    })
                }, 1000);
            }
            else {
                console.error(`Error: ${response}`);
            }
        } else {
            console.error('Upload error:', xhr.statusText);
        }
    };

    // Handle errors
    xhr.onerror = () => {
        console.error('Upload error:', xhr.statusText);
    };

    const formData = new FormData();
    formData.append('file', file);
    xhr.send(formData);
}