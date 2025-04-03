// This script handles interactions on the file page.
// It manages the export of selected courses into a DOCX document
// and allows users to start a new upload.

// Wait until the DOM is fully loaded.
document.addEventListener('DOMContentLoaded', function() {
    // Get button elements and checkbox elements from the page.
    const uploadAgainBtn = document.getElementById('uploadBtn');
    const exportBtn = document.getElementById('exportBtn');
    const checkboxes = document.querySelectorAll('.premium-checkbox');

    // When the "Upload Again" button is clicked, redirect to the homepage.
    uploadAgainBtn.addEventListener('click', function() {
        window.location.href = '/';
    });

    // Handle DOCX export process when the export button is clicked.
    exportBtn.addEventListener('click', function(e) {
        e.preventDefault();

        // Create an object to hold selected courses and their columns.
        const selectedCourses = {};
        // For each course item in the page, gather the checked options.
        document.querySelectorAll('.list-group-item').forEach(item => {
            // Extract the course name from the heading (assuming the first text node is the course name).
            const courseName = item.querySelector('h5').childNodes[0].textContent.trim();
            // Get all checkboxes that are checked within the item.
            const checkedBoxes = item.querySelectorAll('input[type="checkbox"]:checked');
            // Build an array of selected column values.
            const selectedColumns = Array.from(checkedBoxes).map(cb => cb.value);
            
            // Only add the course if at least one column is selected.
            if (selectedColumns.length > 0) {
                selectedCourses[courseName] = selectedColumns;
            }
        });

        // Send the selected courses to the server as JSON to trigger DOCX export.
        fetch('/file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            // file_id should be available as a global variable defined elsewhere in the HTML.
            body: JSON.stringify({ file_id, selectedCourses })
        })
        .then(response => response.blob())
        .then(blob => {
            // Once the DOCX is ready, create a download link and trigger a download.
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            // Set the downloaded filename.
            a.download = 'extracted_data.docx';
            document.body.appendChild(a);
            a.click();
            // Clean up the URL object.
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            // Log any errors that occur during the export process.
            console.error('Error exporting data:', error);
        });

        // Reset checkboxes so that no options remain selected after export.
        checkboxes.forEach(cb => {
            cb.checked = false;
        });
    });
});