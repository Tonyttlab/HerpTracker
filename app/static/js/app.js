/* HerpTracker - Frontend JavaScript */

// ============ Toast Notifications ============
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============ Image Preview ============
function previewImage(input) {
    const preview = document.getElementById('image-preview');
    const placeholder = document.getElementById('placeholder-icon');
    let img = document.getElementById('preview-img');

    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function (e) {
            if (!img) {
                img = document.createElement('img');
                img.id = 'preview-img';
                if (placeholder) placeholder.remove();
                preview.appendChild(img);
            }
            img.src = e.target.result;
        };

        reader.readAsDataURL(input.files[0]);
    }
}

// ============ Reptile CRUD ============
async function saveReptile(event) {
    event.preventDefault();

    const form = document.getElementById('reptile-form');
    const mode = form.dataset.mode;
    const reptileId = form.dataset.reptileId;

    const formData = new FormData(form);

    try {
        let url = '/api/reptile';
        let method = 'POST';

        if (mode === 'edit') {
            url = `/api/reptile/${reptileId}`;
            method = 'PUT';
        }

        const response = await fetch(url, {
            method: method,
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showToast(mode === 'edit' ? 'Reptile updated!' : 'Reptile added!', 'success');
            setTimeout(() => {
                window.location.href = `/reptile/${data.reptile.id}`;
            }, 500);
        } else {
            showToast(data.error || 'Something went wrong', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to save reptile', 'error');
    }
}

async function deleteReptile(reptileId) {
    if (!confirm('Are you sure you want to delete this reptile? All records will be permanently deleted.')) {
        return;
    }

    try {
        const response = await fetch(`/api/reptile/${reptileId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showToast('Reptile deleted', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 500);
        } else {
            showToast(data.error || 'Failed to delete', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to delete reptile', 'error');
    }
}

// ============ Records ============
async function addRecord(event, recordType, reptileId) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    // Handle checkbox for shedding
    if (recordType === 'shedding') {
        const completeCheckbox = form.querySelector('input[name="complete"]');
        formData.set('complete', completeCheckbox.checked ? 'true' : 'false');
    }

    try {
        const response = await fetch(`/api/reptile/${reptileId}/${recordType}`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showToast(`${recordType.charAt(0).toUpperCase() + recordType.slice(1)} recorded!`, 'success');
            // Reload to show updated stats and records
            setTimeout(() => {
                window.location.reload();
            }, 500);
        } else {
            showToast(data.error || 'Failed to add record', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to add record', 'error');
    }
}

async function deleteRecord(recordType, recordId) {
    if (!confirm('Are you sure you want to delete this record?')) {
        return;
    }

    try {
        const response = await fetch(`/api/${recordType}/${recordId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showToast('Record deleted', 'success');
            // Save the current tab before reloading
            const activeTab = document.querySelector('.tab-btn.active');
            if (activeTab) {
                const tabName = activeTab.textContent.toLowerCase().trim();
                localStorage.setItem('activeRecordTab', tabName);
            }
            setTimeout(() => {
                window.location.reload();
            }, 500);
        } else {
            showToast(data.error || 'Failed to delete', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to delete record', 'error');
    }
}

function openEditModal(recordType, recordId, recordData) {
    const modal = document.getElementById('edit-modal');
    const form = document.getElementById('edit-record-form');
    const title = document.getElementById('edit-modal-title');

    // Set the form data
    form.dataset.recordType = recordType;
    form.dataset.recordId = recordId;

    // Set title
    title.textContent = `Edit ${recordType.charAt(0).toUpperCase() + recordType.slice(1)}`;

    // Clear previous fields container
    const fieldsContainer = document.getElementById('edit-fields-container');
    fieldsContainer.innerHTML = '';

    // Convert datetime for input
    const recordedAt = recordData.recorded_at ? recordData.recorded_at.replace('T', 'T').slice(0, 16) : '';

    // Add datetime field
    fieldsContainer.innerHTML += `
        <div class="form-group">
            <label for="edit-recorded-at">Date & Time</label>
            <input type="datetime-local" id="edit-recorded-at" name="recorded_at" value="${recordedAt}">
        </div>
    `;

    // Add type-specific fields
    if (recordType === 'feeding') {
        fieldsContainer.innerHTML += `
            <div class="form-group">
                <label for="edit-food-type">Food Type</label>
                <input type="text" id="edit-food-type" name="food_type" value="${recordData.food_type || ''}">
            </div>
        `;
    } else if (recordType === 'shedding') {
        fieldsContainer.innerHTML += `
            <div class="form-group">
                <label class="checkbox-label">
                    <input type="checkbox" name="complete" ${recordData.complete ? 'checked' : ''}>
                    Complete shed
                </label>
            </div>
        `;
    } else if (recordType === 'measurement') {
        fieldsContainer.innerHTML += `
            <div class="form-row">
                <div class="form-group">
                    <label for="edit-length">Length (cm)</label>
                    <input type="number" id="edit-length" name="length_cm" step="0.1" value="${recordData.length_cm || ''}">
                </div>
                <div class="form-group">
                    <label for="edit-weight">Weight (g)</label>
                    <input type="number" id="edit-weight" name="weight_g" step="0.1" value="${recordData.weight_g || ''}">
                </div>
            </div>
        `;
    }

    if (recordType === 'cleaning') {
        fieldsContainer.innerHTML += `
            <div class="form-group">
                <label for="edit-cleaning-type">Cleaning Type</label>
                <select id="edit-cleaning-type" name="cleaning_type" style="width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-family: inherit; margin-top: 0.5rem;">
                    <option value="spot" ${recordData.cleaning_type === 'spot' ? 'selected' : ''}>Spot Clean</option>
                    <option value="full" ${recordData.cleaning_type === 'full' ? 'selected' : ''}>Full Clean</option>
                </select>
            </div>
        `;
    }

    // Add notes field for all types
    fieldsContainer.innerHTML += `
        <div class="form-group">
            <label for="edit-notes">Notes</label>
            <textarea id="edit-notes" name="notes" rows="2">${recordData.notes || ''}</textarea>
        </div>
    `;

    modal.classList.add('active');
}

function closeEditModal() {
    const modal = document.getElementById('edit-modal');
    modal.classList.remove('active');
}

async function saveRecordEdit(event) {
    event.preventDefault();

    const form = document.getElementById('edit-record-form');
    const recordType = form.dataset.recordType;
    const recordId = form.dataset.recordId;
    const formData = new FormData(form);

    // Handle checkbox for shedding
    if (recordType === 'shedding') {
        const completeCheckbox = form.querySelector('input[name="complete"]');
        formData.set('complete', completeCheckbox.checked ? 'true' : 'false');
    }

    try {
        const response = await fetch(`/api/${recordType}/${recordId}`, {
            method: 'PUT',
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showToast('Record updated!', 'success');
            closeEditModal();
            setTimeout(() => {
                window.location.reload();
            }, 500);
        } else {
            showToast(data.error || 'Failed to update record', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to update record', 'error');
    }
}

// ============ Tabs ============
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');

    // Activate button
    event.target.classList.add('active');
}

// ============ Initialize ============
document.addEventListener('DOMContentLoaded', function () {
    // Set default datetime for record forms to now
    const datetimeInputs = document.querySelectorAll('input[type="datetime-local"]');
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    const localISOTime = now.toISOString().slice(0, 16);

    datetimeInputs.forEach(input => {
        if (!input.value) {
            input.value = localISOTime;
        }
    });

    // Restore saved tab after delete/edit operation
    const savedTab = localStorage.getItem('activeRecordTab');
    if (savedTab) {
        localStorage.removeItem('activeRecordTab');
        // Find and click the matching tab button
        const tabButtons = document.querySelectorAll('.tab-btn');
        tabButtons.forEach(btn => {
            if (btn.textContent.toLowerCase().trim() === savedTab) {
                btn.click();
            }
        });
    }
});
