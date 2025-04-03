// This script handles file upload actions, updates the UI with progress,
// and redirects the user once the PDF processing is complete.

// Select the file input element and the card that triggers the file chooser.
const fileInput = document.getElementById('pdfUpload');
const uploadCard = document.getElementById('uploadCard');

// When the file input value changes, start the file upload process.
fileInput.addEventListener('change', () => handleFileUpload());
// When the upload card is clicked, trigger the file input element.
uploadCard.addEventListener('click', () => fileInput.click());

/**
 * Initiates the file upload process:
 * - Retrieves the selected file.
 * - Updates the UI elements (file name, progress bar, etc.).
 * - Sends the file as a FormData to the backend using XMLHttpRequest.
 * - Polls the server for processing progress and redirects upon completion.
 */
async function handleFileUpload() {
    // Get the selected file from the input.
    const file = fileInput.files[0];
    
    // Get UI elements needed for displaying upload progress.
    const uploadIcon = document.getElementById('uploadIcon');
    const uploadTitle = document.getElementById('uploadTitle');
    const uploadSubtitle = document.getElementById('uploadSubtitle');
    const progressSection = document.getElementById('progressSection');
    const progressBar = document.getElementById('progressBar');
    const statusText = document.getElementById('uploadStatus');
    const cardBody = fileInput.closest('.card-body');

    if (!file) {
        // If no file is selected, exit the function.
        return;
    }

    // Update UI: Hide upload icon, show file name and progress bar.
    uploadIcon.style.display = 'none';
    uploadTitle.textContent = file.name;
    uploadTitle.style.fontSize = '1rem';
    uploadSubtitle.style.display = 'none';
    progressSection.style.display = 'block';
    progressBar.style.width = '0%';
    progressBar.setAttribute('aria-valuenow', 0);
    cardBody.style.pointerEvents = 'none'; // Prevent duplicate submissions

    // Create a new XMLHttpRequest for file upload.
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/', true);

    // Update the progress bar during file upload.
    xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            progressBar.style.width = percentComplete + '%';
            progressBar.setAttribute('aria-valuenow', percentComplete);
        }
    };

    // Handle response once upload completes.
    xhr.onload = () => {
        if (xhr.status === 200) {
            let response = JSON.parse(xhr.responseText);
            // If a file_id is received, the PDF processing has started.
            if (response.file_id) {
                let formData = new FormData();
                formData.append('file_id', response.file_id);
                statusText.innerText = 'Processing PDF...';
                progressBar.style.width = '0%';

                // Poll the server every second for processing progress.
                let progressInterval = setInterval(() => {
                    fetch("/", { method: 'POST', body: formData })
                    .then(response => response.json())
                    .then(data => {
                        progressBar.style.width = data.progress + '%';
                        progressBar.setAttribute('aria-valuenow', data.progress);
                        // Once processing reaches 100%, redirect to the file view.
                        if (data.progress == 100) {
                            clearInterval(progressInterval);
                            window.location.href = data.redirect_url;
                        }
                    });
                }, 3000);
            } else {
                // Log any errors received from the backend.
                console.error(`Error: ${response}`);
            }
        } else {
            console.error('Upload error:', xhr.statusText);
        }
    };

    // Handle network errors.
    xhr.onerror = () => {
        console.error('Upload error:', xhr.statusText);
    };

    // Create FormData, append selected file, and send the request.
    const formData = new FormData();
    formData.append('file', file);
    xhr.send(formData);
}