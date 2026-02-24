// ToastyVotes JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Custom radio button handling for voting form
    const customRadios = document.querySelectorAll('.custom-radio');
    
    customRadios.forEach(radio => {
        radio.addEventListener('click', function() {
            const radioInput = this.querySelector('input[type="radio"]');
            const radioGroup = document.querySelectorAll(`.custom-radio input[name="${radioInput.name}"]`);
            
            // Unselect all radios in this group
            radioGroup.forEach(input => {
                input.closest('.custom-radio').classList.remove('selected');
            });
            
            // Select this radio
            this.classList.add('selected');
            radioInput.checked = true;
        });
    });
    
    // Unhide vote counts (admin feature) with 3-second timer
    const unhideButton = document.getElementById('unhide-votes');
    
    if (unhideButton) {
        unhideButton.addEventListener('click', function() {
            const voteCountElements = document.querySelectorAll('.vote-count');
            
            voteCountElements.forEach(el => {
                el.classList.add('visible');
            });
            
            // Disable the button temporarily
            unhideButton.disabled = true;
            
            // Re-enable after 3.5 seconds (animation is 3 seconds)
            setTimeout(() => {
                voteCountElements.forEach(el => {
                    el.classList.remove('visible');
                });
                unhideButton.disabled = false;
            }, 3500);
        });
    }
    
    // Close polls button with confirmation
    const closeButton = document.getElementById('close-polls');
    
    if (closeButton) {
        closeButton.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to close the polls? This cannot be undone.')) {
                e.preventDefault();
                return false;
            }
            
            const url = this.dataset.url;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = this.dataset.redirect;
                }
            })
            .catch(error => {
                console.error('Error closing polls:', error);
            });
        });
    }
    
    // Copy voting link to clipboard
    const copyLinkBtn = document.getElementById('copy-link');
    
    if (copyLinkBtn) {
        copyLinkBtn.addEventListener('click', function() {
            const linkText = this.dataset.link;
            navigator.clipboard.writeText(linkText).then(
                function() {
                    // Change button text temporarily
                    const originalText = copyLinkBtn.textContent;
                    copyLinkBtn.textContent = 'Copied!';
                    copyLinkBtn.classList.add('btn-success');
                    copyLinkBtn.classList.remove('btn-outline-primary');
                    
                    setTimeout(() => {
                        copyLinkBtn.textContent = originalText;
                        copyLinkBtn.classList.remove('btn-success');
                        copyLinkBtn.classList.add('btn-outline-primary');
                    }, 2000);
                },
                function() {
                    alert('Failed to copy link');
                }
            );
        });
    }

    // Handle alert dismissal
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const closeBtn = alert.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                alert.remove();
            });
            
            // Auto dismiss after 5 seconds
            setTimeout(() => {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 300);
            }, 5000);
        }
    });
});
