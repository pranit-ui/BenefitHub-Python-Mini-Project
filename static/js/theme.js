document.addEventListener('DOMContentLoaded', function() {
    const themeIcon = document.getElementById('theme-icon');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    function setTheme(theme) {
        if (themeIcon) {
            document.body.className = theme;
            themeIcon.textContent = theme === 'dark-theme' ? '☀️' : '🌙';
            localStorage.setItem('theme', theme);
        }
    }

    // Check for saved theme preference or use system preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        setTheme(savedTheme);
    } else {
        setTheme(prefersDarkScheme.matches ? 'dark-theme' : 'light-theme');
    }

    // Theme toggle function
    window.toggleTheme = function() {
        const currentTheme = document.body.className;
        setTheme(currentTheme === 'dark-theme' ? 'light-theme' : 'dark-theme');
    };
});