// Teacher Profile Management JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('teacher-profile-form');
    const alertContainer = document.getElementById('alertContainer');
    const loading = document.getElementById('loading');

    // Load existing profile data when page loads
    loadProfile();

    // Handle form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        console.log('Form submitted!');
        saveProfile();
    });

    async function loadProfile() {
        try {
            const response = await fetch('/api/profile', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success && data.profile) {
                // Populate form with existing data
                populateForm(data.profile);
                showAlert('Profile loaded successfully!', 'success');
            }
        } catch (error) {
            console.error('Error loading profile:', error);
            // Don't show error for new users who don't have a profile yet
        }
    }

    function populateForm(profile) {
        // School name
        document.getElementById('school_name').value = profile.school_name || '';

        // Gender
        if (profile.gender) {
            const genderRadio = document.querySelector(`input[name="gender"][value="${profile.gender}"]`);
            if (genderRadio) genderRadio.checked = true;
        }

        // Board
        if (profile.board) {
            document.getElementById('board').value = profile.board;
        }

        // Grades taught
        if (profile.grades_taught && Array.isArray(profile.grades_taught)) {
            profile.grades_taught.forEach(grade => {
                const checkbox = document.querySelector(`input[name="grades_taught"][value="${grade}"]`);
                if (checkbox) checkbox.checked = true;
            });
        }

        // Languages
        if (profile.languages && Array.isArray(profile.languages)) {
            profile.languages.forEach(language => {
                const checkbox = document.querySelector(`input[name="languages"][value="${language}"]`);
                if (checkbox) checkbox.checked = true;
            });
        }

        // Bio
        document.getElementById('bio').value = profile.bio || '';
    }

    async function saveProfile() {
        console.log('saveProfile function called');
        // Show loading
        loading.style.display = 'block';
        hideAlerts();

        try {
            // Collect form data
            const formData = new FormData(form);
            const profileData = {
                school_name: formData.get('school_name'),
                gender: formData.get('gender'),
                board: formData.get('board'),
                grades_taught: formData.getAll('grades_taught'),
                languages: formData.getAll('languages'),
                bio: formData.get('bio')
            };

            // Validate required fields
            const requiredFields = ['school_name', 'board', 'grades_taught', 'languages'];
            for (const field of requiredFields) {
                if (!profileData[field] || 
                    (Array.isArray(profileData[field]) && profileData[field].length === 0)) {
                    showAlert(`${field.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} is required`, 'danger');
                    loading.style.display = 'none';
                    return;
                }
            }

            console.log('Sending profile data:', profileData);
            
            // Send to server
            const response = await fetch('/api/profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(profileData)
            });

            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Response data:', data);

            if (data.success) {
                showAlert('Profile updated successfully! Redirecting to dashboard...', 'success');
                // Redirect to dashboard after 2 seconds
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 2000);
            } else {
                showAlert(data.error || 'Failed to save profile', 'danger');
            }

        } catch (error) {
            console.error('Error saving profile:', error);
            showAlert('Network error. Please try again.', 'danger');
        } finally {
            loading.style.display = 'none';
        }
    }

    function showAlert(message, type) {
        // Create popup notification
        const popup = document.createElement('div');
        popup.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#d4edda' : '#f8d7da'};
            color: ${type === 'success' ? '#155724' : '#721c24'};
            border: 1px solid ${type === 'success' ? '#c3e6cb' : '#f5c6cb'};
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            z-index: 10000;
            max-width: 300px;
            font-family: 'Poppins', sans-serif;
        `;
        
        popup.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}" style="font-size: 1.2rem;"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(popup);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (popup.parentNode) {
                popup.remove();
            }
        }, 5000);
        
        // Also add to alert container for consistency
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
            ${message}
        `;
        alertContainer.appendChild(alertDiv);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    function hideAlerts() {
        const alerts = alertContainer.querySelectorAll('.alert');
        alerts.forEach(alert => alert.remove());
    }
}); 