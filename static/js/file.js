document.addEventListener('DOMContentLoaded', function() {
    const uploadAgainBtn = document.getElementById('uploadBtn');
    const exportBtn = document.getElementById('exportBtn');
    const checkboxes = document.querySelectorAll('.premium-checkbox');

    uploadAgainBtn.addEventListener('click', function() {
        window.location.href = '/';
    });

    exportBtn.addEventListener('click', function(e) {        
        e.preventDefault();
        
        const selectedCourses = {};
        document.querySelectorAll('.list-group-item').forEach(item => {
            const courseName = item.querySelector('h5').childNodes[0].textContent.trim();
            const checkedBoxes = item.querySelectorAll('input[type="checkbox"]:checked');
            const selectedColumns = Array.from(checkedBoxes).map(cb => cb.value);
            
            if (selectedColumns.length > 0) {
                selectedCourses[courseName] = selectedColumns;
            }
        });

        fetch('/file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file_id, selectedCourses })
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'file.docx';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => console.error('Error exporting data:', error));

        checkboxes.forEach(cb => {
            cb.checked = false;
        });
    });
});