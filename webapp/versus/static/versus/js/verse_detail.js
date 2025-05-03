document.addEventListener('DOMContentLoaded', function() {
    // Get all tab buttons
    const tabButtons = document.querySelectorAll('[data-view-toggle]');
    
    // Add click handlers
    tabButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all buttons
            tabButtons.forEach(btn => {
                btn.classList.remove('active');
                document.querySelector(btn.dataset.viewToggle).classList.remove('show', 'active');
            });
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Show the target view
            const target = document.querySelector(this.dataset.viewToggle);
            if (target) {
                target.classList.add('show', 'active');
            }
        });
    });
}); 