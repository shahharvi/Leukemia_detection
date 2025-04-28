document.addEventListener('DOMContentLoaded', function() {
    const patientDetailModal = document.getElementById('patientDetailModal');
    const closeModalButtons = document.getElementsByClassName('close-modal');
    const searchInput = document.getElementById('patientSearch');
    const searchBtn = document.getElementById('searchBtn');
    const diagnosisFilter = document.getElementById('diagnosisFilter');
    const applyFiltersBtn = document.getElementById('applyFilters');
    const patientTableBody = document.getElementById('patientTableBody');
    let currentPatientId = null;

    // Perform search
    function performSearch() {
        const searchTerm = searchInput.value.trim();
        const leukemiaType = diagnosisFilter.value || '';
        console.log(`Searching: term="${searchTerm}", type="${leukemiaType}"`);

        if (!searchInput) {
            console.error('Search input element not found');
            patientTableBody.innerHTML = '<tr><td colspan="6">Error: Search input not found</td></tr>';
            return;
        }

        fetch(`/api/patients/search?search=${encodeURIComponent(searchTerm)}&leukemia_type=${encodeURIComponent(leukemiaType)}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        })
        .then(response => {
            console.log('Search response status:', response.status);
            if (!response.ok) throw new Error(`HTTP error: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log('Search data:', data);
            if (!data.success) {
                patientTableBody.innerHTML = `<tr><td colspan="6">${data.message || data.error || 'No patients found'}</td></tr>`;
                return;
            }
            updatePatientTable(data.patients);
        })
        .catch(error => {
            console.error('Search error:', error);
            patientTableBody.innerHTML = `<tr><td colspan="6">Error: ${error.message}</td></tr>`;
        });
    }

    // Update patient table
    function updatePatientTable(patients) {
        patientTableBody.innerHTML = '';
        if (!patients || patients.length === 0) {
            patientTableBody.innerHTML = '<tr><td colspan="6">No patients found</td></tr>';
            return;
        }
        patients.forEach(patient => {
            console.log('Rendering patient:', patient);
            const testDate = patient.test_date || 'N/A';
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${patient.patient_id || 'N/A'}</td>
                <td>${patient.patient_name || 'Unknown'}</td>
                <td>${patient.age || 'N/A'}</td>
                <td>${patient.leukemia_type || 'Pending'}</td>
                <td>${testDate}</td>
                <td>
                    <button class="btn-action view-btn" data-id="${patient.patient_id}">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            `;
            patientTableBody.appendChild(row);
        });
        attachViewButtonListeners();
    }

    // Attach view button listeners
    function attachViewButtonListeners() {
        const viewButtons = document.getElementsByClassName('view-btn');
        console.log(`Found ${viewButtons.length} view buttons`);
        Array.from(viewButtons).forEach(button => {
            button.removeEventListener('click', viewPatientDetails);
            button.addEventListener('click', viewPatientDetails);
            console.log(`Attached listener to button with data-id: ${button.getAttribute('data-id')}`);
        });
    }

    // View patient details
    function viewPatientDetails(event) {
        currentPatientId = event.target.closest('button').getAttribute('data-id');
        console.log('Viewing patient ID:', currentPatientId);
        if (!currentPatientId) {
            console.error('No patient ID found on button');
            alert('Error: No patient ID found');
            return;
        }

        fetch(`/api/patient/${encodeURIComponent(currentPatientId)}`, {
            method: 'GET',
            credentials: 'include'
        })
        .then(response => {
            console.log('View response status:', response.status);
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || `HTTP error: ${response.status}`);
                }).catch(() => {
                    throw new Error(`HTTP error: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('View data:', data);
            if (!data.success) {
                throw new Error(data.error || 'Failed to fetch patient');
            }
            if (!data.patient) {
                throw new Error('Patient data missing in response');
            }
            displayPatientDetails(data.patient, data.remarks || []);
            patientDetailModal.style.display = 'block';
        })
        .catch(error => {
            console.error('View error:', error.message || error);
            alert(`Error loading patient details: ${error.message || 'Unknown error'}`);
        });
    }

    // Display patient details
    function displayPatientDetails(patient, remarks) {
        console.log('Displaying patient:', patient, 'Remarks:', remarks);
        document.getElementById('patientName').textContent = patient.patient_name || 'Unknown';
        document.getElementById('patientId').textContent = `#${patient.patient_id || 'N/A'}`;
        document.getElementById('patientAge').textContent = patient.age || 'N/A';
        document.getElementById('patientGender').textContent = patient.gender || 'N/A';
        document.getElementById('patientContact').textContent = patient.contact || 'N/A';
        document.getElementById('patientEmail').textContent = patient.email || 'N/A';
        document.getElementById('testDate').textContent = patient.test_date || 'N/A';
        document.getElementById('leukemiaType').textContent = patient.leukemia_type || 'Pending';
        document.getElementById('confidenceScore').textContent = patient.confidence_score ? 
            `${(patient.confidence_score * 100).toFixed(1)}%` : 'N/A';

        const remarksContainer = document.getElementById('patientRemarks');
        remarksContainer.innerHTML = remarks && remarks.length > 0 ? 
            remarks.map(r => `<div class="remark-item"><p>${r.remark_text}</p><small>${r.created_at || 'N/A'}</small></div>`).join('') : 
            '<p>No remarks available</p>';
    }

    // Event listeners
    if (searchBtn) {
        searchBtn.addEventListener('click', performSearch);
    } else {
        console.error('Search button not found');
    }

    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', performSearch);
    } else {
        console.error('Apply filters button not found');
    }

    if (searchInput) {
        searchInput.addEventListener('keypress', (e) => e.key === 'Enter' && performSearch());
    } else {
        console.error('Search input not found');
    }

    Array.from(closeModalButtons).forEach(btn => btn.addEventListener('click', () => patientDetailModal.style.display = 'none'));
    window.addEventListener('click', (e) => e.target === patientDetailModal && (patientDetailModal.style.display = 'none'));

    // Initial load
    performSearch();
});