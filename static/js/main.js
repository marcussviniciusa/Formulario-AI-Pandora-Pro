// Form validation
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Password strength validation
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            const hasUpperCase = /[A-Z]/.test(password);
            const hasNumber = /[0-9]/.test(password);
            const hasSymbol = /[!@#$%^&*(),.?":{}|<>]/.test(password);
            const isLongEnough = password.length >= 8;

            let strength = 0;
            if (hasUpperCase) strength++;
            if (hasNumber) strength++;
            if (hasSymbol) strength++;
            if (isLongEnough) strength++;

            const feedback = this.nextElementSibling;
            if (feedback && feedback.classList.contains('text-muted')) {
                switch(strength) {
                    case 0:
                    case 1:
                        feedback.style.color = '#dc3545';
                        break;
                    case 2:
                    case 3:
                        feedback.style.color = '#ffc107';
                        break;
                    case 4:
                        feedback.style.color = '#28a745';
                        break;
                }
            }
        });
    }

    // Phone number formatting
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            let x = e.target.value.replace(/\D/g, '').match(/(\d{0,2})(\d{0,5})(\d{0,4})/);
            e.target.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? '-' + x[3] : '');
        });
    }
});
