document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registrationForm');
    const pages = document.querySelectorAll('.form-page');
    const steps = document.querySelectorAll('.step');
    const nextBtns = document.querySelectorAll('.next-btn');
    const prevBtns = document.querySelectorAll('.prev-btn');
    let currentPage = 0;

    // Next button click
    nextBtns.forEach(button => {
        button.addEventListener('click', () => {
            if (validatePage(currentPage)) {
                pages[currentPage].classList.add('hidden');
                currentPage++;
                pages[currentPage].classList.remove('hidden');
                updateProgress();
            }
        });
    });

    // Previous button click
    prevBtns.forEach(button => {
        button.addEventListener('click', () => {
            pages[currentPage].classList.add('hidden');
            currentPage--;
            pages[currentPage].classList.remove('hidden');
            updateProgress();
        });
    });

    // Update progress bar
    function updateProgress() {
        steps.forEach((step, idx) => {
            if (idx <= currentPage) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
    }

    // Validate each page
    function validatePage(pageIndex) {
        const currentPageElement = pages[pageIndex];
        const inputs = currentPageElement.querySelectorAll('input[required], select[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value) {
                isValid = false;
                input.classList.add('error');
            } else {
                input.classList.remove('error');
            }
        });

        return isValid;
    }

    // Handle file input
    function getBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    }

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!validatePage(currentPage)) {
            return;
        }

        try {
            const formData = new FormData(form);
            
            const response = await fetch('/submit', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (result.success) {
                alert('Registration successful!');
                window.location.href = 'index.html';
            } else {
                throw new Error(result.message || 'Submission failed');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });

    // Add error styling
    const style = document.createElement('style');
    style.textContent = `
        .error {
            border-color: red !important;
        }
    `;
    document.head.appendChild(style);
});

// Add this code to your form.js file, likely near the end where form submission is handled

document.getElementById('registrationForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    if (!validatePage(currentPage)) {
        return;
    }
    
    const formData = new FormData(this);
    
    fetch('/submit', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Create and show success popup
            const popup = document.createElement('div');
            popup.className = 'success-popup';
            popup.innerHTML = `
                <div class="popup-content">
                    <i class="fas fa-check-circle"></i>
                    <h2>Registration Successful!</h2>
                    <p>Thank you for registering. You will be redirected to the home page shortly.</p>
                </div>
            `;
            document.body.appendChild(popup);
            
            // Redirect after 3 seconds
            setTimeout(() => {
                window.location.href = '/';
            }, 3000);
        } else {
            alert('Registration failed: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during registration. Please try again.');
    });
});