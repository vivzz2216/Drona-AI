document.addEventListener('DOMContentLoaded', function() {
    // Theme toggling functionality
    initThemeToggle();
    
    // Initialize form submission with loading animation
    initFormSubmission();
    
    // Initialize tooltips if Bootstrap's tooltip is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        initTooltips();
    }
    
    // Initialize the player comparison visualization if players are compared
    initPlayerComparison();

    // Add animation to sidebar icons
    initSidebarAnimations();
    
    // Add responsive navigation behavior
    initResponsiveNav();
});

/**
 * Initialize theme toggle functionality
 */
function initThemeToggle() {
    const themeToggle = document.querySelector('.theme-toggle');
    if (!themeToggle) return;
    
    themeToggle.addEventListener('click', function() {
        const body = document.body;
        const currentTheme = body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        // Add a transition class for smooth theme change
        body.classList.add('theme-transition');
        
        // Update theme attribute
        body.setAttribute('data-theme', newTheme);
        
        // Update toggle button text and icon
        this.innerHTML = newTheme === 'dark'
            ? '<i class="fas fa-moon"></i> Dark Mode'
            : '<i class="fas fa-sun"></i> Light Mode';
        
        // Save preference to localStorage
        localStorage.setItem('theme', newTheme);
        
        // Remove transition class after animation completes
        setTimeout(() => {
            body.classList.remove('theme-transition');
        }, 1000);
    });
    
    // Load saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.setAttribute('data-theme', savedTheme);
    themeToggle.innerHTML = savedTheme === 'dark'
        ? '<i class="fas fa-moon"></i> Dark Mode'
        : '<i class="fas fa-sun"></i> Light Mode';
}

/**
 * Initialize form submission with loading animation
 */
function initFormSubmission() {
    const compareForm = document.getElementById('compareForm');
    const loadingOverlay = document.getElementById('loadingOverlay');
    
    if (!compareForm || !loadingOverlay) return;
    
    compareForm.addEventListener('submit', function(event) {
        // Check if both players are selected and different
        const player1 = this.querySelector('select[name="player1"]').value;
        const player2 = this.querySelector('select[name="player2"]').value;
        
        if (player1 === player2 && player1 !== '') {
            event.preventDefault();
            showAlert('Please select two different players to compare', 'error');
            return;
        }
        
        if (player1 && player2) {
            event.preventDefault();
            loadingOverlay.style.display = 'flex';
            
            // Simulate phrases during loading
            const loadingPhrases = [
                'Analyzing player statistics...',
                'Comparing tactical profiles...',
                'Evaluating performance metrics...',
                'Processing matchday data...',
                'Generating performance insights...'
            ];
            
            const loadingSubtext = document.querySelector('.loading-subtext');
            let phraseIndex = 0;
            
            // Update phrase every 2 seconds
            const phraseInterval = setInterval(() => {
                loadingSubtext.textContent = loadingPhrases[phraseIndex];
                phraseIndex = (phraseIndex + 1) % loadingPhrases.length;
            }, 2000);
            
            // Submit the form after a delay
            setTimeout(() => {
                clearInterval(phraseInterval);
                compareForm.submit();
            }, 2000);
        }
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize player comparison visualization
 */
function initPlayerComparison() {
    const comparisonContainer = document.querySelector('.comparison-container');
    if (!comparisonContainer) return;
    
    // Add animation to player cards
    const playerCards = document.querySelectorAll('.player-card');
    playerCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 300 + (index * 200));
    });
    
    // Highlight better stats
    highlightBetterStats();
    
    // Initialize radar charts if available
    if (typeof initRadarCharts === 'function' && document.querySelectorAll('.radar-chart-container').length > 0) {
        initRadarCharts();
    }
}

/**
 * Highlight better stats by comparing values
 */
function highlightBetterStats() {
    const statRows = document.querySelectorAll('.stat-row');
    
    statRows.forEach(row => {
        const better = row.getAttribute('data-better') || 'higher';
        const player1Value = parseFloat(row.querySelector('.player1-stat').textContent);
        const player2Value = parseFloat(row.querySelector('.player2-stat').textContent);
        
        if (!isNaN(player1Value) && !isNaN(player2Value)) {
            if (better === 'higher') {
                if (player1Value > player2Value) {
                    row.querySelector('.player1-stat').classList.add('better');
                    row.querySelector('.player2-stat').classList.add('worse');
                } else if (player2Value > player1Value) {
                    row.querySelector('.player2-stat').classList.add('better');
                    row.querySelector('.player1-stat').classList.add('worse');
                }
            } else if (better === 'lower') {
                if (player1Value < player2Value) {
                    row.querySelector('.player1-stat').classList.add('better');
                    row.querySelector('.player2-stat').classList.add('worse');
                } else if (player2Value < player1Value) {
                    row.querySelector('.player2-stat').classList.add('better');
                    row.querySelector('.player1-stat').classList.add('worse');
                }
            }
        }
    });
}

/**
 * Initialize sidebar animations
 */
function initSidebarAnimations() {
    const sidebarIcons = document.querySelectorAll('.sidebar i');
    
    sidebarIcons.forEach((icon, index) => {
        icon.style.opacity = '0';
        icon.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            icon.style.transition = 'opacity 0.5s ease, transform 0.5s ease, color 0.3s ease';
            icon.style.opacity = '1';
            icon.style.transform = 'translateX(0)';
        }, 100 + (index * 100));
    });
}

/**
 * Initialize responsive navigation
 */
function initResponsiveNav() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (!navbarToggler || !navbarCollapse) return;
    
    // Close mobile nav when clicking outside
    document.addEventListener('click', function(event) {
        const isNavbarOpen = navbarCollapse.classList.contains('show');
        const clickedInsideNav = navbarCollapse.contains(event.target) || navbarToggler.contains(event.target);
        
        if (isNavbarOpen && !clickedInsideNav) {
            // Create a new click event on the toggler to close the navbar
            const clickEvent = new MouseEvent('click', {
                bubbles: true,
                cancelable: true,
                view: window
            });
            navbarToggler.dispatchEvent(clickEvent);
        }
    });
}

/**
 * Show alert message
 * @param {string} message - Alert message text
 * @param {string} type - Alert type (success, error, warning, info)
 */
function showAlert(message, type = 'info') {
    // Create alert element
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    alertElement.style.top = '20px';
    alertElement.style.right = '20px';
    alertElement.style.zIndex = '1050';
    alertElement.style.maxWidth = '300px';
    alertElement.setAttribute('role', 'alert');
    
    // Set content
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to body
    document.body.appendChild(alertElement);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        alertElement.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(alertElement);
        }, 300);
    }, 5000);
}
