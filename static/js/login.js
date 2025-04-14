document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('loginModal');
    const loginBtn = document.getElementById('loginBtn');
    const closeBtn = document.querySelector('.close');
    const loginForm = document.getElementById('loginForm');
    const alertSuccess = document.getElementById('alertSuccess');
    const alertError = document.getElementById('alertError');
    const registerForm = document.getElementById('registerForm');
    const showRegisterForm = document.getElementById('showRegisterForm');
    const showLoginForm = document.getElementById('showLoginForm');

    function showAlert(element, message) {
        element.textContent = message;
        element.style.display = 'block';
        setTimeout(() => {
            element.style.display = 'none';
        }, 3000);
    }

    function resetForm() {
        loginForm.reset();
        alertSuccess.style.display = 'none';
        alertError.style.display = 'none';
    }

    function switchForms(showForm, hideForm) {
        hideForm.style.display = 'none';
        showForm.style.display = 'block';
        resetForm();
    }

    if (showRegisterForm) {
        showRegisterForm.onclick = function(e) {
            e.preventDefault();
            switchForms(registerForm, loginForm);
        };
    }

    if (showLoginForm) {
        showLoginForm.onclick = function(e) {
            e.preventDefault();
            switchForms(loginForm, registerForm);
        };
    }

    if (loginBtn) {
        loginBtn.onclick = function() {
            modal.style.display = 'block';
        };
    }

    if (closeBtn) {
        closeBtn.onclick = function() {
            modal.style.display = 'none';
            resetForm();
        };
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
            resetForm();
        }
    };

    if (loginForm) {
        loginForm.onsubmit = async function(e) {
            e.preventDefault();
            
            try {
                const formData = new FormData(loginForm);
                const response = await fetch('/login', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                const data = await response.json();
                
                if (data.success) {
                    showAlert(alertSuccess, data.message);
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    showAlert(alertError, data.message);
                }
            } catch (error) {
                console.error('Error:', error);
                showAlert(alertError, 'An error occurred. Please try again.');
            }
        };
    }

    if (registerForm) {
        registerForm.onsubmit = async function(e) {
            e.preventDefault();
            
            const password = document.getElementById('reg_password').value;
            const confirmPassword = document.getElementById('reg_confirm_password').value;
            
            if (password !== confirmPassword) {
                showAlert(alertError, 'Passwords do not match');
                return;
            }
            
            try {
                const formData = new FormData(registerForm);
                const response = await fetch('/register', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                const data = await response.json();
                
                if (data.success) {
                    showAlert(alertSuccess, data.message);
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    showAlert(alertError, data.message);
                }
            } catch (error) {
                console.error('Error:', error);
                showAlert(alertError, 'An error occurred. Please try again.');
            }
        };
    }
});