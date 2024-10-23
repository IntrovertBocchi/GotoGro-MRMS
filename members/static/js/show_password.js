// Function to toggle password visibility
document.addEventListener("DOMContentLoaded", function () {
    // Function to toggle the password field
    const togglePassword = (id) => {
        const passwordField = document.getElementById(id);
        const toggleIcon = document.querySelector(`[data-toggle="${id}"] i`);

        if (passwordField.type === "password") {
            passwordField.type = "text";
            toggleIcon.classList.remove('fa-eye');
            toggleIcon.classList.add('fa-eye-slash');
        } else {
            passwordField.type = "password";
            toggleIcon.classList.remove('fa-eye-slash');
            toggleIcon.classList.add('fa-eye');
        }
    };

    // Add event listener to the eye icon
    document.querySelectorAll('[data-toggle]').forEach(function (toggleButton) {
        toggleButton.addEventListener('click', function () {
            const target = this.getAttribute('data-toggle');
            togglePassword(target);
        });
    });
});
