document.addEventListener('DOMContentLoaded', function() {
    // File upload display
    const fileInput = document.getElementById('blood_test_file');
    const fileNameDisplay = document.getElementById('file-name');
    
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            if (this.files && this.files[0]) {
                const fileSize = this.files[0].size / 1024; // Convert to KB
                const maxSize = 162; // Maximum file size in KB
                
                if (fileSize > maxSize) {
                    alert(`File size exceeds the limit of ${maxSize}KB. Your file is ${fileSize.toFixed(2)}KB.`);
                    this.value = ''; // Clear the file input
                    fileNameDisplay.textContent = '';
                    fileNameDisplay.classList.remove('file-selected');
                } else {
                    fileNameDisplay.textContent = this.files[0].name + ` (${fileSize.toFixed(2)}KB)`;
                    fileNameDisplay.classList.add('file-selected');
                }
            } else {
                fileNameDisplay.textContent = '';
                fileNameDisplay.classList.remove('file-selected');
            }
        });
    }
    
    // Form validation
    const predictionForm = document.querySelector('.input-section form');
    if (predictionForm) {
        predictionForm.addEventListener('submit', function(e) {
            const patientName = document.getElementById('patient_name').value;
            const age = document.getElementById('age').value;
            const gender = document.getElementById('gender').value;
            const testDate = document.getElementById('test_date').value;
            const fileInput = document.getElementById('blood_test_file');
            
            if (!patientName || !age || !gender || !testDate) {
                e.preventDefault();
                alert('Please fill in all required fields.');
                return false;
            }
            
            if (!fileInput.files || fileInput.files.length === 0) {
                e.preventDefault();
                alert('Please upload a blood test file.');
                return false;
            }
            
            // Check file type
            const fileName = fileInput.files[0].name;
            const fileExt = fileName.split('.').pop().toLowerCase();
            
            if (!['csv', 'xls', 'xlsx'].includes(fileExt)) {
                e.preventDefault();
                alert('Only .csv, .xls, or .xlsx files are allowed.');
                return false;
            }
            
            // Check file size again (in KB)
            const fileSize = fileInput.files[0].size / 1024;
            const maxSize = 162; // Maximum file size in KB
            
            if (fileSize > maxSize) {
                e.preventDefault();
                alert(`File size exceeds the limit of ${maxSize}KB. Your file is ${fileSize.toFixed(2)}KB.`);
                return false;
            }
            
            return true;
        });
    }
});